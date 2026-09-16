# Chapter 5 - Replay a Recorded Case

This folder is self-contained. It runs the unchanged incident agent against tool
functions backed by the Chapter 4 recording.

```bash
python run_replay.py
```

| File | Purpose |
|---|---|
| `agent.py` | The agent from Chapter 1, unchanged. |
| `scenarios/checkout-latency.json` | The complete recorded scenario. |
| `scenario.py` | The Chapter 4 scenario loader. |
| `replay.py` | Builds tool-compatible functions from recorded responses. |
| `run_replay.py` | Wires the recording, replay tools, and agent together. |