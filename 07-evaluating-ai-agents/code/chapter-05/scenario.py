"""Load and validate one recorded evaluation scenario."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class Situation:
    alert: Dict[str, str]
    tool_responses: Dict[str, Any]


@dataclass(frozen=True)
class AnswerKey:
    true_category: str
    true_cause: str
    required_evidence: List[str]
    distraction: str
    max_steps: int


@dataclass(frozen=True)
class Validity:
    owner: str
    recorded_at: str
    review_by: str
    assumptions: Dict[str, str]


@dataclass(frozen=True)
class Scenario:
    id: str
    validity: Validity
    situation: Situation
    answer_key: AnswerKey


def _require_keys(value: Dict[str, Any], keys: set, location: str) -> None:
    missing = keys - value.keys()
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"{location} is missing: {names}")


def load_scenario(path: Path) -> Scenario:
    raw = json.loads(path.read_text(encoding="utf-8"))
    _require_keys(raw, {"id", "validity", "situation", "answer_key"}, "scenario")
    _require_keys(raw["validity"], {"owner", "recorded_at", "review_by", "assumptions"}, "validity")
    if not raw["validity"]["assumptions"]:
        raise ValueError("validity.assumptions must not be empty")
    _require_keys(raw["situation"], {"alert", "tool_responses"}, "situation")
    _require_keys(
        raw["answer_key"],
        {"true_category", "true_cause", "required_evidence", "distraction", "max_steps"},
        "answer_key",
    )
    if raw["answer_key"]["max_steps"] < 1:
        raise ValueError("answer_key.max_steps must be at least 1")
    return Scenario(
        id=raw["id"],
        validity=Validity(**raw["validity"]),
        situation=Situation(**raw["situation"]),
        answer_key=AnswerKey(**raw["answer_key"]),
    )