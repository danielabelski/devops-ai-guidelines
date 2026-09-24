"""Offline Jev transport fakes test status handling, not model accuracy."""

import unittest
from dataclasses import replace

from agent import Agent
from agent_input import load_agent_input
from answer_key import load_answer_key
from jev_judge import build_request, evaluate
from replay import build_replay_tools
from run_agent import CASE, CASES
from run_judge import DEMO_POLICY
from test_agent import EXPLANATION, careful_calls, fake_client, response_for


def sample_response(model="jev-1.13.0", unsupported=0.05):
    return {
        "model": model,
        "answers": {
            "explanation_quality": {
                "type": "score", "score": 2.0, "confidence": 1.0,
                "legend": {"0": "wrong", "1": "partial", "2": "clear"},
                "probabilities": {"0": 0.0, "1": 0.0, "2": 1.0},
            },
            "unsupported_claim": {"type": "noul", "noul": unsupported},
        },
        "usage": {"input_tokens": 300, "output_tokens": 50},
    }


class JudgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        agent_input = load_agent_input(CASE)
        cls.answer = load_answer_key(CASE)
        cls.conclusion = Agent(
            fake_client(*careful_calls()), build_replay_tools(agent_input), "gpt-4.1-mini"
        ).run(agent_input.alert)

    def judge(self, response):
        return evaluate(self.conclusion, self.answer, lambda payload: response, DEMO_POLICY)

    def test_valid_judge_and_hard_gates_pass(self):
        result = self.judge(sample_response())
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["hard"]["passed"])

    def test_hard_failure_cannot_be_rescued(self):
        conclusion = replace(self.conclusion, evidence=[])
        result = evaluate(conclusion, self.answer, lambda payload: sample_response(), DEMO_POLICY)
        self.assertEqual(result["status"], "fail")

    def test_model_change_is_incomplete(self):
        self.assertEqual(self.judge(sample_response(model="jev-next"))["status"], "incomplete")

    def test_unsupported_claim_fails(self):
        self.assertEqual(self.judge(sample_response(unsupported=0.9))["status"], "fail")

    def test_transport_failure_is_incomplete(self):
        def unavailable(payload):
            raise OSError("network unavailable")

        result = evaluate(self.conclusion, self.answer, unavailable, DEMO_POLICY)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["reason"], "judge_transport_error")

    def test_http_failure_reports_only_status_code(self):
        from urllib.error import HTTPError

        def forbidden(payload):
            raise HTTPError("https://api.cloudflare.com/", 403, "forbidden", {}, None)

        result = evaluate(self.conclusion, self.answer, forbidden, DEMO_POLICY)
        self.assertEqual(result["reason"], "cloudflare_http_403")

    def test_secret_bearing_answer_never_reaches_transport(self):
        sent = []
        conclusion = replace(self.conclusion, root_cause="Bearer secret-value")
        result = evaluate(conclusion, self.answer, lambda payload: sent.append(payload), DEMO_POLICY)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["reason"], "judge_input_rejected")
        self.assertEqual(sent, [])

    def test_request_contains_only_observed_data(self):
        request = build_request(self.conclusion, self.answer, lambda state: state)
        self.assertEqual(set(request["state"]["observed_tool_responses"]), {
            "get_metrics", "get_logs", "get_deploys", "get_db_status"
        })
        self.assertNotIn("answer_key", request["state"])
        self.assertNotIn("lines", request["state"]["observed_tool_responses"]["get_logs"])

    def test_new_cases_have_approved_judge_inputs(self):
        for label in ("dependency", "capacity"):
            with self.subTest(case=label):
                case = CASES[label]
                agent_input = load_agent_input(case)
                answer = load_answer_key(case)
                calls = [
                    response_for(name, {"service": agent_input.alert["service"]})
                    for name in ("get_metrics", "get_logs", "get_deploys", "get_db_status")
                ]
                calls.append(response_for("submit_diagnosis", {
                    "root_cause": answer.true_cause,
                    "category": answer.true_category,
                    "cause_change": answer.cause_change,
                    "cause_effect": answer.cause_effect,
                    "evidence": answer.required_evidence,
                    "rejected_signals": [answer.distraction_id],
                }))
                conclusion = Agent(
                    fake_client(*calls), build_replay_tools(agent_input), "gpt-4.1-mini"
                ).run(agent_input.alert)
                self.assertEqual(
                    evaluate(conclusion, answer, lambda payload: sample_response(), DEMO_POLICY)["status"],
                    "pass",
                )


if __name__ == "__main__":
    unittest.main()