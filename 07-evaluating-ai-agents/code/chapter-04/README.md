# Chapter 4 - Record a Test Case

This folder is self-contained. It records one incident as data and validates the
record before later chapters use it.

```bash
python check_scenario.py
```

| File | Purpose |
|---|---|
| `scenarios/checkout-latency.json` | The frozen situation and separate answer key. |
| `scenario.py` | Typed records and a loader that rejects missing fields. |
| `check_scenario.py` | Loads the scenario and prints a short inventory. |