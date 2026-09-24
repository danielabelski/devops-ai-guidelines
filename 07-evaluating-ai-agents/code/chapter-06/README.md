# Chapter 6 - Keep the Answer Away from the Agent

This folder is self-contained. The runtime loads `AgentInput`; the grader-side
module loads `AnswerKey`. The agent run never constructs or receives the latter.
The runner checks validity first, using a demo system manifest that must be
replaced by independently maintained current-system data in real use.

```bash
python run_isolated.py
python -m unittest test_case.py
```

| File | Purpose |
|---|---|
| `agent.py` | The agent from Chapter 1, unchanged. |
| `scenario_types.py` | Separate `AgentInput` and `AnswerKey` types. |
| `agent_input.py` | Runtime loader for situation data only. |
| `answer_key.py` | Grader-only loader, unused during the agent run. |
| `replay.py` | Builds tools from `AgentInput`. |
| `validity.py` | Rejects expired or mismatched cases before agent input is built. |
| `run_isolated.py` | Shows the runtime input has no answer-key field. |
| `test_case.py` | Checks expiry, isolation, and a replayed timeout. |