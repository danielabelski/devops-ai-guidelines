"""Load the answer only after the agent has committed to a conclusion."""

import json
from pathlib import Path

from scenario_types import AnswerKey


def load_answer_key(path: Path) -> AnswerKey:
    raw = json.loads(path.read_text(encoding="utf-8"))
    required = set(AnswerKey.__dataclass_fields__) - {"scenario_id"}
    if not required <= raw["answer_key"].keys():
        raise ValueError(f"answer_key is missing: {', '.join(sorted(required - raw['answer_key'].keys()))}")
    if raw["answer_key"]["max_steps"] < 1:
        raise ValueError("answer_key.max_steps must be at least 1")
    return AnswerKey(scenario_id=raw["id"], **raw["answer_key"])