"""Load the recorded case and show what it contains."""

from pathlib import Path

from scenario import load_scenario


scenario = load_scenario(Path("scenarios/checkout-latency.json"))

print(f"Scenario:          {scenario.id}")
print(f"Alert:             {scenario.situation.alert['message']}")
print(f"Recorded tools:    {', '.join(scenario.situation.tool_responses)}")
print(f"True category:     {scenario.answer_key.true_category}")
print(f"Required evidence: {', '.join(scenario.answer_key.required_evidence)}")
print(f"Step budget:       {scenario.answer_key.max_steps}")