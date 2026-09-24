# Chapter 7 - Score with Hard Gates

Self-contained snapshot. A local demo inventory supplies the current-system IDs;
real evaluations must obtain them independently from the target environment.

```bash
python run_grade.py
python -m unittest test_grade.py
```

`run_grade.py` prints gate results for a careful, lucky, and misled agent. `grade.py`
checks the cause, real tool calls plus citations, the logged distraction, and the
case's step budget. `agent.py` keeps runner-recorded observations for the grader.
`agent_input.py` and `answer_key.py` preserve the Chapter 6 boundary; the answer
is loaded after each run. `validity.py` rejects expired cases before replay.