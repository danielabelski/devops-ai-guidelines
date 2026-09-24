"""Focused checks for case validity and the agent input boundary."""

import unittest
from datetime import date
from pathlib import Path

from agent_input import load_agent_input
from replay import build_replay_tools
from scenario_types import AgentInput
from validity import ExpiredCase, check_case


CASE = Path(__file__).parent / "scenarios/checkout-latency.json"
CURRENT_SYSTEM = {
    "topology": "checkout-db-pool-v1",
    "runbook": "checkout-latency-v2",
    "tool_contract": "incident-tools-v1",
}


class CaseTests(unittest.TestCase):
    def test_current_case_has_only_agent_visible_fields(self):
        check_case(CASE, CURRENT_SYSTEM, today=date(2026, 9, 24))
        agent_input = load_agent_input(CASE)
        self.assertEqual(set(vars(agent_input)), {"scenario_id", "alert", "tool_responses"})

    def test_changed_assumption_expires_case(self):
        changed = dict(CURRENT_SYSTEM, topology="checkout-db-pool-v2")
        with self.assertRaises(ExpiredCase):
            check_case(CASE, changed, today=date(2026, 9, 24))

    def test_unknown_assumption_expires_case(self):
        with self.assertRaises(ExpiredCase):
            check_case(CASE, {}, today=date(2026, 9, 24))

    def test_overdue_review_expires_case(self):
        with self.assertRaises(ExpiredCase):
            check_case(CASE, CURRENT_SYSTEM, today=date(2026, 12, 13))

    def test_replay_can_raise_recorded_error(self):
        agent_input = AgentInput(
            scenario_id="tool-timeout",
            alert={"service": "checkout-service"},
            tool_responses={
                "get_logs": {
                    "service": "checkout-service",
                    "raises": "TimeoutError",
                    "message": "logs unavailable",
                }
            },
        )
        with self.assertRaisesRegex(TimeoutError, "logs unavailable"):
            build_replay_tools(agent_input)["get_logs"]("checkout-service")


if __name__ == "__main__":
    unittest.main()