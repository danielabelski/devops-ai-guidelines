"""Build tool functions backed by a recorded situation."""

from copy import deepcopy

from scenario import Situation


def build_replay_tools(situation: Situation):
    """Return one callable for every recorded tool response."""
    tools = {}

    for tool_name, recorded_response in situation.tool_responses.items():
        def replay(service, response=recorded_response):
            if service != response.get("service"):
                raise ValueError(
                    f"recorded response is for {response.get('service')}, not {service}"
                )
            return deepcopy(response)

        tools[tool_name] = replay

    return tools