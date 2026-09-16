"""Run the unchanged agent against recorded tools."""

from pathlib import Path

from agent import Agent
from replay import build_replay_tools
from scenario import load_scenario


def scripted_model(alert, observations):
    if "get_metrics" not in observations:
        return {"type": "call_tool", "tool": "get_metrics"}
    if "get_deploys" not in observations:
        return {"type": "call_tool", "tool": "get_deploys"}
    if "get_db_status" not in observations:
        return {"type": "call_tool", "tool": "get_db_status"}
    return {
        "type": "conclude",
        "root_cause": "14:02 deploy cut DB_MAX_CONNECTIONS 50->5, exhausting the pool",
        "category": "deploy",
        "evidence": ["get_deploys", "get_db_status"],
    }


scenario = load_scenario(Path("scenarios/checkout-latency.json"))
tools = build_replay_tools(scenario.situation)
agent = Agent(tools=tools, call_model=scripted_model)
conclusion = agent.run(scenario.situation.alert)

print(f"Scenario:   {scenario.id}")
print(f"Root cause: {conclusion.root_cause}")
print(f"Category:   {conclusion.category}")
print(f"Evidence:   {', '.join(conclusion.evidence)}")
print(f"Steps:      {len(conclusion.trajectory)}")