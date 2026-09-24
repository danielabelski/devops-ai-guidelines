"""Run the unchanged agent against recorded tools."""

from pathlib import Path

from agent import Agent
from replay import build_replay_tools
from scenario import load_scenario
from validity import check_validity


def scripted_model(alert, observations):
    if "get_metrics" not in observations:
        return {"type": "call_tool", "tool": "get_metrics"}
    if "get_logs" not in observations:
        return {"type": "call_tool", "tool": "get_logs"}
    if "get_deploys" not in observations:
        return {"type": "call_tool", "tool": "get_deploys"}
    if "get_db_status" not in observations:
        return {"type": "call_tool", "tool": "get_db_status"}
    change = observations["get_deploys"]["deploys"][0]["change"]
    pool = observations["get_db_status"]
    caused_by_pool = "DB_MAX_CONNECTIONS" in change and pool["waiting"] > 0
    return {
        "type": "conclude",
        "root_cause": f"Deploy changed {change}; {pool['waiting']} requests wait for the pool" if caused_by_pool else "Cause unknown",
        "category": "deploy" if caused_by_pool else "unknown",
        "evidence": ["get_deploys", "get_db_status"] if caused_by_pool else [],
    }


scenario = load_scenario(Path("scenarios/checkout-latency.json"))
current_system = {
    "topology": "checkout-db-pool-v1",
    "runbook": "checkout-latency-v2",
    "tool_contract": "incident-tools-v1",
}
check_validity(scenario.validity, current_system)
tools = build_replay_tools(scenario.situation)
agent = Agent(tools=tools, call_model=scripted_model)
conclusion = agent.run(scenario.situation.alert)

print(f"Scenario:   {scenario.id}")
print(f"Root cause: {conclusion.root_cause}")
print(f"Category:   {conclusion.category}")
print(f"Evidence:   {', '.join(conclusion.evidence)}")
print(f"Steps:      {len(conclusion.trajectory)}")