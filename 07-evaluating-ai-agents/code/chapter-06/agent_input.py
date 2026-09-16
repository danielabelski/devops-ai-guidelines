"""Load only the data allowed to enter an agent run."""

import json
from pathlib import Path

from scenario_types import AgentInput


def load_agent_input(path: Path) -> AgentInput:
    raw = json.loads(path.read_text(encoding="utf-8"))
    situation = raw["situation"]
    return AgentInput(
        scenario_id=raw["id"],
        alert=situation["alert"],
        tool_responses=situation["tool_responses"],
    )