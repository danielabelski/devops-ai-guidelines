"""Check whether a recorded case still describes the target system."""

from datetime import date


class ExpiredCase(ValueError):
    pass


def check_validity(validity, current_system, today=None):
    today = today or date.today()
    if today > date.fromisoformat(validity.review_by):
        raise ExpiredCase(f"review due on {validity.review_by}")
    for name, expected in validity.assumptions.items():
        actual = current_system.get(name)
        if actual != expected:
            raise ExpiredCase(f"{name}: expected {expected}, current {actual}")