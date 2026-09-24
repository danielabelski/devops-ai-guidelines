"""Load grader-only truth. Agent runtime code must not import this module."""

import json
from pathlib import Path

from scenario_types import AnswerKey


def load_answer_key(path: Path) -> AnswerKey:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not {"id", "answer_key"} <= raw.keys():
        raise ValueError("scenario needs id and answer_key")
    required = {"true_category", "true_cause", "required_evidence", "distraction", "max_steps"}
    if not required <= raw["answer_key"].keys():
        raise ValueError("answer_key is incomplete")
    if raw["answer_key"]["max_steps"] < 1:
        raise ValueError("answer_key.max_steps must be at least 1")
    return AnswerKey(scenario_id=raw["id"], **raw["answer_key"])