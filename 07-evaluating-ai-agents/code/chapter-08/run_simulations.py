"""Run each numbered simulation with the real agent and Jev, then compare the results."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from answer_key import load_answer_key
from config import load_settings
from grade import grade
from jev_judge import call_cloudflare, evaluate
from run_agent import CASES, run_agent
from run_judge import DEMO_POLICY


SIMULATIONS = Path(__file__).parent / "scenarios/simulations"
REPORT = Path(__file__).parent / "simulation-results.json"
FIELDS = {"id", "case", "change", "instructions", "max_steps"}


def load_simulation(path):
    simulation = json.loads(path.read_text(encoding="utf-8"))
    if (
        not FIELDS <= simulation.keys() <= FIELDS | {"alert_message"}
        or simulation["id"] != path.stem
        or simulation["case"] not in CASES
        or not isinstance(simulation["instructions"], str) or not simulation["instructions"].strip()
        or type(simulation["max_steps"]) is not int or not 1 <= simulation["max_steps"] <= 8
    ):
        raise ValueError(f"{path.name} is not a valid simulation")
    return simulation


def run_simulation(simulation, settings, judge):
    record = {"id": simulation["id"], "change": simulation["change"], "case": simulation["case"]}
    try:
        case = CASES[simulation["case"]]
        agent_input, conclusion = run_agent(
            settings,
            case_path=case,
            alert_message=simulation.get("alert_message"),
            instructions=simulation["instructions"],
            max_steps=simulation["max_steps"],
        )
        answer = load_answer_key(case)
        if agent_input.scenario_id != answer.scenario_id:
            raise ValueError("answer belongs to another case")
        record.update({
            "alert": conclusion.alert["message"],
            "tool_calls": [s["tool"] for s in conclusion.trajectory if s["type"] == "call_tool"],
            "root_cause": conclusion.root_cause,
            "category": conclusion.category,
            "cause_change": conclusion.cause_change,
            "cause_effect": conclusion.cause_effect,
            "cited_evidence": conclusion.evidence,
            "rejected_signals": conclusion.rejected_signals,
            "steps": len(conclusion.trajectory),
        })
        if judge:
            result = evaluate(
                conclusion, answer, lambda payload: call_cloudflare(payload, settings), DEMO_POLICY
            )
        else:
            result = {"status": "not_judged", "hard": grade(conclusion, answer)}
        record["hard_gates"] = result["hard"]["gates"]
        record["status"] = result["status"]
        if "reason" in result:
            record["judge_reason"] = result["reason"]
        if "judge" in result:
            record["jev"] = {
                "model": result["judge"]["model"],
                "explanation_score": result["judge"]["quality"]["score"],
                "confidence": result["judge"]["quality"]["confidence"],
                "unsupported_claim": result["judge"]["unsupported"]["noul"],
            }
    except Exception as error:
        record["status"] = "error"
        record["error_type"] = type(error).__name__
    return record


def show(record):
    print(f"\n{record['id']}  ({record['case']})  {record['change']}")
    if record["status"] == "error":
        print(f"  error: {record['error_type']}")
        return
    print(f"  alert:     {record['alert']}")
    print(f"  tools:     {' -> '.join(record['tool_calls']) or '(none)'}  ({record['steps']} steps)")
    print(f"  answer:    {record['root_cause']}")
    print(f"  change:    {record['cause_change']!r}  effect: {record['cause_effect']}")
    print(f"  evidence:  {', '.join(record['cited_evidence']) or '(none)'}")
    print(f"  rejected:  {', '.join(record['rejected_signals']) or '(none)'}")
    print("  gates:     " + "  ".join(
        f"{name} {'PASS' if ok else 'FAIL'}" for name, ok in record["hard_gates"].items()
    ))
    if "jev" in record:
        jev = record["jev"]
        print(
            f"  Jev ({jev['model']}): explanation {jev['explanation_score']:.2f}"
            f" (confidence {jev['confidence']:.2f}), unsupported claim {jev['unsupported_claim']:.2f}"
        )
    if "judge_reason" in record:
        print(f"  Jev:       no answer ({record['judge_reason']})")
    print(f"  result:    {record['status'].upper()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-judge", action="store_true", help="Skip Jev and show hard gates only")
    parser.add_argument("--only", nargs="*", help="Simulation ids to run, such as checkout-latency-01")
    args = parser.parse_args()
    settings = load_settings(require_jev=not args.no_judge)
    simulations = [load_simulation(path) for path in sorted(SIMULATIONS.glob("checkout-latency-*.json"))]
    if args.only:
        simulations = [s for s in simulations if s["id"] in args.only]
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(lambda s: run_simulation(s, settings, not args.no_judge), simulations))
    print(f"Agent model: {settings.openai_model}")
    for record in records:
        show(record)
    print("\nSummary")
    print(f"  {'simulation':<22}{'cause':<7}{'evid':<6}{'distr':<7}{'steps':<7}{'Jev':<7}result")
    for record in records:
        gates = record.get("hard_gates", {})
        marks = [("ok" if gates.get(name) else "x") for name in ("cause", "evidence", "distraction", "steps")]
        score = f"{record['jev']['explanation_score']:.2f}" if "jev" in record else "-"
        print(f"  {record['id']:<22}{marks[0]:<7}{marks[1]:<6}{marks[2]:<7}{marks[3]:<7}{score:<7}{record['status']}")
    REPORT.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"\nFull run record: {REPORT.name}")


if __name__ == "__main__":
    main()
