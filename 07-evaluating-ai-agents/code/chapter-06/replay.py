"""Build tool functions backed only by agent-visible input."""

from copy import deepcopy

from scenario_types import AgentInput


def build_replay_tools(agent_input: AgentInput):
    tools = {}

    for tool_name, recorded_response in agent_input.tool_responses.items():
        def replay(service, response=recorded_response):
            if service != response.get("service"):
                raise ValueError(
                    f"recorded response is for {response.get('service')}, not {service}"
                )
            return deepcopy(response)

        tools[tool_name] = replay

    return tools