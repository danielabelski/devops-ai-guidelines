"""Run an agent using only the scenario's agent-visible input."""

from dataclasses import asdict
from pathlib import Path

from agent import Agent
from agent_input import load_agent_input
from replay import build_replay_tools
from validity import check_case


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


path = Path("scenarios/checkout-latency.json")
current_system = {
    "topology": "checkout-db-pool-v1",
    "runbook": "checkout-latency-v2",
    "tool_contract": "incident-tools-v1",
}
check_case(path, current_system)
agent_input = load_agent_input(path)
visible_fields = asdict(agent_input)
assert "answer_key" not in visible_fields

tools = build_replay_tools(agent_input)
agent = Agent(tools=tools, call_model=scripted_model)
conclusion = agent.run(agent_input.alert)

print(f"Agent can see: {', '.join(visible_fields)}")
print("Agent can see answer key: no")
print(f"Conclusion category: {conclusion.category}")
print("Answer key is not passed to the agent.")