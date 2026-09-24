"""Compare alert wording on the same frozen incident across multiple real runs."""

import argparse
import json
from pathlib import Path

from answer_key import load_answer_key
from config import load_settings
from grade import grade
from run_agent import CASE, run_agent


ALERT_VARIANTS = {
    "original": "checkout-service p95 latency > 2s",
    "timeline": "checkout-service p95 latency exceeded 2 seconds at 14:03. Diagnose from the recorded signals.",
    "evidence": "checkout-service p95 latency exceeded 2 seconds at 14:03. Explain what changed and cite the evidence for your diagnosis.",
}
REPORT = Path(__file__).parent / "trial-results.json"


def collect_trials(settings, runs):
    records = []
    for variant, message in ALERT_VARIANTS.items():
        for attempt in range(1, runs + 1):
            record = {"variant": variant, "attempt": attempt, "alert_message": message}
            try:
                agent_input, conclusion = run_agent(settings, alert_message=message)
                answer = load_answer_key(CASE)
                if agent_input.scenario_id != answer.scenario_id:
                    raise ValueError("answer belongs to another case")
                hard = grade(conclusion, answer)
                record.update({
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
    parser.add_argument("--runs", type=int, default=2, help="Runs per alert variant, from 1 to 10")
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        parser.error("--runs must be between 1 and 10")
    settings = load_settings()
    records = collect_trials(settings, args.runs)
    REPORT.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    for variant in ALERT_VARIANTS:
        attempts = [record for record in records if record["variant"] == variant]
        passed = sum(record.get("hard_passed", False) for record in attempts)
        errors = sum("error_type" in record for record in attempts)
        print(f"{variant}: {passed}/{len(attempts)} hard-gate passes, {errors} errors")
    print(f"Full run record: {REPORT}")
    if any("error_type" in record for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()