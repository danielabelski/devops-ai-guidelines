"""Compare a careful diagnosis, a lucky guess, and a misleading signal."""

from pathlib import Path

from agent import Agent
from agent_input import load_agent_input
from answer_key import load_answer_key
from grade import grade
from replay import build_replay_tools
from validity import check_case


CASE = Path(__file__).parent / "scenarios/checkout-latency.json"
# This is a demo inventory; a real runner obtains these IDs independently.
CURRENT_SYSTEM = {
    "topology": "checkout-db-pool-v1",
    "runbook": "checkout-latency-v2",
    "tool_contract": "incident-tools-v1",
}


def careful_model(alert, observations):
    for name in ("get_metrics", "get_logs", "get_deploys", "get_db_status"):
        if name not in observations:
            return {"type": "call_tool", "tool": name}
    change = observations["get_deploys"]["deploys"][0]["change"]
    pool = observations["get_db_status"]
    exhausted = pool["in_use"] == pool["pool_size"] and pool["waiting"] > 0
    later_payment = any(
        "payment-provider" in line and line[:5] > alert["started_at"]
        for line in observations["get_logs"]["lines"]
    )
    return {
        "type": "conclude",
        "root_cause": f"The deploy changed {change}, exhausting the pool and delaying checkout" if exhausted else "Cause unknown",
        "category": "deploy" if exhausted else "unknown",
        "cause_change": change if exhausted else "",
        "cause_effect": "pool_exhausted" if exhausted else "",
        "evidence": ["get_deploys", "get_db_status"] if exhausted else [],
        "rejected_signals": ["payment_provider"] if later_payment and exhausted else [],
    }


def lucky_model(alert, observations):
    return {
        "type": "conclude", "root_cause": "Probably a deploy",
        "category": "deploy", "cause_change": "DB_MAX_CONNECTIONS 50 -> 5",
        "cause_effect": "pool_exhausted", "evidence": ["get_deploys", "get_db_status"],
        "rejected_signals": ["payment_provider"],
    }


def misled_model(alert, observations):
    if "get_logs" not in observations:
        return {"type": "call_tool", "tool": "get_logs"}
    return {
        "type": "conclude", "root_cause": "The payment provider slowed checkout",
        "category": "dependency", "cause_change": "payment_provider",
        "cause_effect": "dependency_slow", "evidence": ["get_logs"],
        "rejected_signals": [],
    }


def main():
    check_case(CASE, CURRENT_SYSTEM)
    agent_input = load_agent_input(CASE)
    tools = build_replay_tools(agent_input)
    for label, model in (("careful", careful_model), ("lucky", lucky_model), ("misled", misled_model)):
        conclusion = Agent(tools, model).run(agent_input.alert)
        answer = load_answer_key(CASE)
        if answer.scenario_id != agent_input.scenario_id:
            raise ValueError("answer belongs to another case")
        result = grade(conclusion, answer)
        print(f"{label}: {'PASS' if result['passed'] else 'FAIL'} {result['gates']}")


if __name__ == "__main__":
    main()