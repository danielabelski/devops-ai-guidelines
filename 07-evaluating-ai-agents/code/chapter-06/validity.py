"""Check case metadata before constructing agent input."""

import json
from datetime import date
from pathlib import Path


class ExpiredCase(ValueError):
    pass


def check_case(path: Path, current_system, today=None):
    metadata = json.loads(path.read_text(encoding="utf-8"))["validity"]
    today = today or date.today()
    if today > date.fromisoformat(metadata["review_by"]):
        raise ExpiredCase(f"review due on {metadata['review_by']}")
    if not metadata["assumptions"]:
        raise ValueError("validity.assumptions must not be empty")
    for name, expected in metadata["assumptions"].items():
        actual = current_system.get(name)
        if actual != expected:
            raise ExpiredCase(f"{name}: expected {expected}, current {actual}")