# Chapter 5 - Replay a Recorded Case

This folder is self-contained. It runs the unchanged incident agent against tool
functions backed by the Chapter 4 recording.
`run_replay.py` checks the case's assumptions before it runs. Its `current_system`
dictionary is a demo fixture, not a live inventory; a real runner must supply
current topology, runbook, and tool contract IDs independently.

```bash
python run_replay.py
```

| File | Purpose |
|---|---|
| `agent.py` | The agent from Chapter 1, unchanged. |
| `scenarios/checkout-latency.json` | The complete recorded scenario. |
| `scenario.py` | The Chapter 4 scenario loader. |
| `replay.py` | Replays one success or named error per tool. |
| `validity.py` | Rejects mismatched assumptions and overdue reviews. |
| `run_replay.py` | Checks validity, then wires replay tools and the agent. |