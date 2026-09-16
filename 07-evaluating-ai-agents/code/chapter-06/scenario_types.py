"""Types shared by the two sides of the evaluation boundary."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class AgentInput:
    scenario_id: str
    alert: Dict[str, str]
    tool_responses: Dict[str, Any]


@dataclass(frozen=True)
class AnswerKey:
    scenario_id: str
    true_category: str
    true_cause: str
    required_evidence: List[str]
    distraction: str
    max_steps: int