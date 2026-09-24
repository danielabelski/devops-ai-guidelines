"""Deterministic checks; no model decides these gates."""

from datetime import time


def grade(conclusion, answer):
    calls = [step["tool"] for step in conclusion.trajectory if step["type"] == "call_tool"]
    consulted = set(calls) & set(conclusion.observations)
    deploys = conclusion.observations.get("get_deploys", {}).get("deploys", [])
    pool = conclusion.observations.get("get_db_status", {})
    try:
        alert_time = time.fromisoformat(conclusion.alert["started_at"])
        supported_change = any(
            deploy.get("change") == answer.cause_change
            and time.fromisoformat(deploy["at"]) <= alert_time
            for deploy in deploys
        )
    except (KeyError, ValueError, TypeError):
        alert_time = None
        supported_change = False
    supported_effect = (
        answer.cause_effect == "pool_exhausted"
        and pool.get("pool_size", 0) > 0
        and pool.get("in_use") == pool.get("pool_size")
        and pool.get("waiting", 0) > 0
    )
    cause = (
        conclusion.category == answer.true_category
        and conclusion.cause_change == answer.cause_change
        and conclusion.cause_effect == answer.cause_effect
        and supported_change
        and supported_effect
    )
    evidence = set(answer.required_evidence) <= consulted
    evidence_claims = set(answer.required_evidence) <= set(conclusion.evidence) <= consulted
    try:
        distraction_seen = alert_time is not None and answer.distraction_source in consulted and any(
            answer.distraction_marker in line and time.fromisoformat(line[:8]) > alert_time
            for line in conclusion.observations[answer.distraction_source].get("lines", [])
        )
    except (KeyError, ValueError, TypeError):
        distraction_seen = False
    distraction_handled = (
        distraction_seen
        and answer.distraction_id in conclusion.rejected_signals
        and answer.distraction_id not in conclusion.cause_change
        and answer.distraction_id not in conclusion.cause_effect
    )
    gates = {
        "cause": cause,
        "evidence": evidence and evidence_claims,
        "distraction": distraction_handled,
        "steps": len(conclusion.trajectory) <= answer.max_steps
        and bool(conclusion.trajectory)
        and conclusion.trajectory[-1]["type"] == "conclude",
    }
    return {"gates": gates, "passed": all(gates.values()), "distraction_seen": distraction_seen}