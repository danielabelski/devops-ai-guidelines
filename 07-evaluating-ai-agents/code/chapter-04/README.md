# Chapter 4 - Record a Test Case

This folder is self-contained. It records one incident, its answer, and the
assumptions under which it remains a useful test. It validates required fields;
it does not check those assumptions against production.

```bash
python check_scenario.py
```

| File | Purpose |
|---|---|
| `scenarios/checkout-latency.json` | The frozen situation, answer key, and validity metadata. |
| `scenario.py` | Typed records and a loader that rejects missing fields. |
| `check_scenario.py` | Loads the scenario and prints a short inventory. |