"""The incident agent from Chapter 1, unchanged."""

from dataclasses import dataclass, field


@dataclass
class Conclusion:
    root_cause: str
    category: str
    evidence: list = field(default_factory=list)
    trajectory: list = field(default_factory=list)


class Agent:
    def __init__(self, tools, call_model, max_steps=6):
        self.tools = tools
        self.call_model = call_model
        self.max_steps = max_steps

    def run(self, alert):
        observations = {}
        trajectory = []

        for _ in range(self.max_steps):
            action = self.call_model(alert, observations)
            trajectory.append(action)

            if action["type"] == "call_tool":
                name = action["tool"]
                observations[name] = self.tools[name](alert["service"])
                continue

            if action["type"] == "conclude":
                return Conclusion(
                    root_cause=action["root_cause"],
                    category=action["category"],
                    evidence=action.get("evidence", []),
                    trajectory=trajectory,
                )

        return Conclusion(
            root_cause="(no conclusion: step budget exhausted)",
            category="unknown",
            evidence=[],
            trajectory=trajectory,
        )