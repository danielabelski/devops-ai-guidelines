"""Regression checks for the four deterministic gates."""

import unittest
from copy import deepcopy
from datetime import date

from agent import Agent
from agent_input import load_agent_input
from answer_key import load_answer_key
from grade import grade
from replay import build_replay_tools
from run_grade import CASE, CURRENT_SYSTEM, careful_model, lucky_model, misled_model
from validity import check_case


class GradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        check_case(CASE, CURRENT_SYSTEM, today=date(2026, 9, 24))
        cls.agent_input = load_agent_input(CASE)
        cls.answer = load_answer_key(CASE)

    def run_model(self, model):
        tools = build_replay_tools(self.agent_input)
        return Agent(tools, model).run(self.agent_input.alert)

    def test_careful_agent_passes(self):
        conclusion = self.run_model(careful_model)
        result = grade(conclusion, self.answer)
        self.assertTrue(result["passed"])
        self.assertTrue(result["distraction_seen"])

    def test_lucky_guess_cannot_fake_tool_calls(self):
        result = grade(self.run_model(lucky_model), self.answer)
        self.assertFalse(result["passed"])
        self.assertFalse(result["gates"]["evidence"])
        self.assertFalse(result["gates"]["distraction"])

    def test_wrong_cause_fails(self):
        result = grade(self.run_model(misled_model), self.answer)
        self.assertFalse(result["gates"]["cause"])
        self.assertFalse(result["gates"]["distraction"])

    def test_unseen_distraction_is_not_rejected(self):
        conclusion = self.run_model(careful_model)
        conclusion.observations.pop("get_logs")
        result = grade(conclusion, self.answer)
        self.assertFalse(result["distraction_seen"])
        self.assertFalse(result["gates"]["distraction"])

    def test_step_budget_is_case_specific(self):
        conclusion = self.run_model(careful_model)
        conclusion.trajectory.insert(0, {"type": "call_tool", "tool": "get_metrics"})
        self.assertFalse(grade(conclusion, self.answer)["gates"]["steps"])

    def test_guessed_cause_fails_against_healthy_pool(self):
        conclusion = self.run_model(careful_model)
        conclusion.observations = deepcopy(conclusion.observations)
        conclusion.observations["get_db_status"]["waiting"] = 0
        self.assertFalse(grade(conclusion, self.answer)["gates"]["cause"])

    def test_deploy_after_alert_cannot_be_cause(self):
        conclusion = self.run_model(careful_model)
        conclusion.observations = deepcopy(conclusion.observations)
        conclusion.observations["get_deploys"]["deploys"][0]["at"] = "14:05"
        self.assertFalse(grade(conclusion, self.answer)["gates"]["cause"])

    def test_payment_line_before_alert_is_not_rejected(self):
        conclusion = self.run_model(careful_model)
        conclusion.observations = deepcopy(conclusion.observations)
        conclusion.observations["get_logs"]["lines"][-1] = "14:01:12 INFO payment-provider latency 180ms"
        result = grade(conclusion, self.answer)
        self.assertFalse(result["distraction_seen"])
        self.assertFalse(result["gates"]["distraction"])


if __name__ == "__main__":
    unittest.main()