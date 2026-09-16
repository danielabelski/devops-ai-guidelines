# Chapter 6 - Keep the Answer Away from the Agent

This folder is self-contained. The runtime loads `AgentInput`; the grader-side
module loads `AnswerKey`. The agent run never constructs or receives the latter.

```bash
python run_isolated.py
```

| File | Purpose |
|---|---|
| `agent.py` | The agent from Chapter 1, unchanged. |
| `scenario_types.py` | Separate `AgentInput` and `AnswerKey` types. |
| `agent_input.py` | Runtime loader for situation data only. |
| `answer_key.py` | Grader-only loader, unused during the agent run. |
| `replay.py` | Builds tools from `AgentInput`. |
| `run_isolated.py` | Proves the runtime input contains no answer key. |