"""Run an agent using only the scenario's agent-visible input."""

from dataclasses import asdict
from pathlib import Path

from agent import Agent
from agent_input import load_agent_input
from replay import build_replay_tools


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


path = Path("scenarios/checkout-latency.json")
agent_input = load_agent_input(path)
visible_fields = asdict(agent_input)
assert "answer_key" not in visible_fields

tools = build_replay_tools(agent_input)
agent = Agent(tools=tools, call_model=scripted_model)
conclusion = agent.run(agent_input.alert)

print(f"Agent can see: {', '.join(visible_fields)}")
print("Agent can see answer key: no")
print(f"Conclusion category: {conclusion.category}")
print("Answer key remains unopened until grading.")