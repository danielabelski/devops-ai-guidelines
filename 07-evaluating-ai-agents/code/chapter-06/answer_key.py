"""Load grader-only truth. Agent runtime code must not import this module."""

import json
from pathlib import Path

from scenario_types import AnswerKey


def load_answer_key(path: Path) -> AnswerKey:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return AnswerKey(scenario_id=raw["id"], **raw["answer_key"])