"""The incident agent with a grader-owned record of what tools returned."""

from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class Conclusion:
    root_cause: str
    category: str
    alert: dict = field(default_factory=dict)
    cause_change: str = ""
    cause_effect: str = ""
    evidence: list = field(default_factory=list)
    rejected_signals: list = field(default_factory=list)
    trajectory: list = field(default_factory=list)
    observations: dict = field(default_factory=dict)


class Agent:
    def __init__(self, tools, call_model, max_steps=6):
        self.tools = tools
        self.call_model = call_model
        self.max_steps = max_steps

    def run(self, alert):
        observations = {}
        trajectory = []
        for _ in range(self.max_steps):
            action = self.call_model(alert, deepcopy(observations))
            trajectory.append(deepcopy(action))
            if action["type"] == "call_tool":
                name = action["tool"]
                observations[name] = self.tools[name](alert["service"])
                continue
            if action["type"] == "conclude":
                return Conclusion(
                    root_cause=action["root_cause"],
                    category=action["category"],
                    alert=deepcopy(alert),
                    cause_change=action.get("cause_change", ""),
                    cause_effect=action.get("cause_effect", ""),
                    evidence=action.get("evidence", []),
                    rejected_signals=action.get("rejected_signals", []),
                    trajectory=trajectory,
                    observations=deepcopy(observations),
                )
        return Conclusion(
            root_cause="(no conclusion: step budget exhausted)",
            category="unknown",
            alert=deepcopy(alert),
            trajectory=trajectory,
            observations=deepcopy(observations),
        )