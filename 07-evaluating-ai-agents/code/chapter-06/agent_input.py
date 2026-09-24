"""Load only the data allowed to enter an agent run."""

import json
from pathlib import Path

from scenario_types import AgentInput


def load_agent_input(path: Path) -> AgentInput:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not {"id", "situation"} <= raw.keys():
        raise ValueError("scenario needs id and situation")
    situation = raw["situation"]
    if not {"alert", "tool_responses"} <= situation.keys():
        raise ValueError("situation needs alert and tool_responses")
    return AgentInput(
        scenario_id=raw["id"],
        alert=situation["alert"],
        tool_responses=situation["tool_responses"],
    )