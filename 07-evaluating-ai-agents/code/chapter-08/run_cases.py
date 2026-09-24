"""Run each synthetic checkout cause and record hard gates without calling Jev."""

import argparse
import json
from pathlib import Path

from answer_key import load_answer_key
from config import load_settings
from grade import grade
from jev_judge import call_cloudflare, evaluate
from run_agent import CASES, run_agent
from run_judge import DEMO_POLICY


REPORT = Path(__file__).parent / "case-results.json"
JUDGE_REPORT = Path(__file__).parent / "case-judge-results.json"


def collect_cases(settings, runs, judge=False):
    records = []
    for label, case in CASES.items():
        for attempt in range(1, runs + 1):
            record = {"case": label, "attempt": attempt, "agent_model": settings.openai_model}
            try:
                agent_input, conclusion = run_agent(settings, case_path=case)
                answer = load_answer_key(case)
                if agent_input.scenario_id != answer.scenario_id:
                    raise ValueError("answer belongs to another case")
                hard = grade(conclusion, answer)
                if judge:
                    evaluated = evaluate(
                        conclusion, answer,
                        lambda payload: call_cloudflare(payload, settings),
                        DEMO_POLICY,
                    )
                    hard = evaluated["hard"]
                    record["evaluation_status"] = evaluated["status"]
                    if "reason" in evaluated:
                        record["judge_reason"] = evaluated["reason"]
                    if "judge" in evaluated:
                        result = evaluated["judge"]
                        record["judge"] = {
                            "model": result["model"],
                            "rubric": result["rubric"],
                            "explanation_score": result["quality"]["score"],
                            "explanation_confidence": result["quality"]["confidence"],
                            "unsupported_claim": result["unsupported"]["noul"],
                        }
                record.update({
                    "scenario_id": agent_input.scenario_id,
                    "alert": conclusion.alert["message"],
                    "category": conclusion.category,
                    "root_cause": conclusion.root_cause,
                    "cause_change": conclusion.cause_change,
                    "cause_effect": conclusion.cause_effect,
                    "tool_calls": [
                        step["tool"] for step in conclusion.trajectory
                        if step["type"] == "call_tool"
                    ],
                    "cited_evidence": conclusion.evidence,
                    "rejected_signals": conclusion.rejected_signals,
                    "steps": len(conclusion.trajectory),
                    "hard_gates": hard["gates"],
                    "hard_passed": hard["passed"],
                })
            except Exception as error:
                record["error_type"] = type(error).__name__
            records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=1, help="Runs per case, from 1 to 5")
    parser.add_argument("--judge", action="store_true", help="Also call Cloudflare Jev for a complete grade")
    args = parser.parse_args()
    if not 1 <= args.runs <= 5:
        parser.error("--runs must be between 1 and 5")
    records = collect_cases(load_settings(require_jev=args.judge), args.runs, judge=args.judge)
    report = JUDGE_REPORT if args.judge else REPORT
    report.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    for label in CASES:
        attempts = [record for record in records if record["case"] == label]
        passed = sum(record.get("hard_passed", False) for record in attempts)
        errors = sum("error_type" in record for record in attempts)
        completed = sum(record.get("evaluation_status") == "pass" for record in attempts)
        result = f", {completed}/{len(attempts)} complete passes" if args.judge else ""
        print(f"{label}: {passed}/{len(attempts)} hard-gate passes{result}, {errors} errors")
    print(f"Full run record: {report}")
    if any("error_type" in record for record in records) or (
        args.judge and any(record.get("evaluation_status") != "pass" for record in records)
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()