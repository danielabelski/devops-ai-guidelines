"""Mocked OpenAI Responses calls exercise the real tool loop without a key."""

import json
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agent import Agent
from agent_input import load_agent_input
from answer_key import load_answer_key
from grade import grade
from replay import build_replay_tools
from run_agent import CURRENT_SYSTEM, run_agent
from validity import check_case


CASE = Path(__file__).parent / "scenarios/checkout-latency.json"
EXPLANATION = "The deploy reduced DB_MAX_CONNECTIONS from 50 to 5, exhausting the pool and causing checkout timeouts"


def response_for(name, arguments):
    return SimpleNamespace(
        status="completed",
        output=[SimpleNamespace(
            type="function_call", name=name, arguments=json.dumps(arguments), call_id=name
        )],
    )


class FakeResponses:
    def __init__(self, calls):
        self.calls = iter(calls)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return next(self.calls)


def fake_client(*calls):
    return SimpleNamespace(responses=FakeResponses(calls))


def careful_calls():
    calls = [
        response_for(name, {"service": "checkout-service"})
        for name in ("get_metrics", "get_logs", "get_deploys", "get_db_status")
    ]
    calls.append(response_for("submit_diagnosis", {
        "root_cause": EXPLANATION,
        "category": "deploy",
        "cause_change": "DB_MAX_CONNECTIONS 50 -> 5",
        "cause_effect": "pool_exhausted",
        "evidence": ["get_deploys", "get_db_status"],
        "rejected_signals": ["payment_provider"],
    }))
    return calls


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent_input = load_agent_input(CASE)

    def test_real_agent_protocol_records_calls_and_observations(self):
        client = fake_client(*careful_calls())
        result = Agent(client, build_replay_tools(self.agent_input), "gpt-4.1-mini").run(self.agent_input.alert)
        self.assertEqual(result.root_cause, EXPLANATION)
        self.assertEqual(result.category, "deploy")
        self.assertEqual(len(result.trajectory), 5)
        self.assertEqual(result.trajectory[-1], {"type": "conclude"})
        self.assertEqual(set(result.observations), {"get_metrics", "get_logs", "get_deploys", "get_db_status"})
        self.assertEqual(len(client.responses.requests), 5)
        self.assertTrue(all(call["store"] is False for call in client.responses.requests))
        self.assertTrue(all(call["tool_choice"] == "required" for call in client.responses.requests))
        self.assertNotIn("answer_key", str(client.responses.requests[0]["input"]))

    def test_service_switch_is_rejected_before_a_tool_runs(self):
        client = fake_client(response_for("get_logs", {"service": "other-service"}))
        with self.assertRaisesRegex(ValueError, "different service"):
            Agent(client, build_replay_tools(self.agent_input), "gpt-4.1-mini").run(self.agent_input.alert)

    def test_no_conclusion_does_not_become_a_pass(self):
        client = fake_client(*[
            response_for("get_metrics", {"service": "checkout-service"}) for _ in range(5)
        ])
        result = Agent(client, build_replay_tools(self.agent_input), "gpt-4.1-mini").run(self.agent_input.alert)
        self.assertEqual(result.category, "unknown")
        self.assertEqual(len(result.trajectory), 5)

    def test_alert_variant_changes_only_the_message(self):
        client = fake_client(*careful_calls())
        settings = SimpleNamespace(openai_api_key="unused", openai_model="gpt-4.1-mini")
        with patch("run_agent.check_case"):
            agent_input, conclusion = run_agent(
                settings, client=client, alert_message="Checkout latency rose at 14:03"
            )
        sent_alert = json.loads(client.responses.requests[0]["input"][1]["content"])
        self.assertEqual(sent_alert["message"], "Checkout latency rose at 14:03")
        self.assertEqual(sent_alert["service"], agent_input.alert["service"])
        self.assertEqual(sent_alert["started_at"], agent_input.alert["started_at"])
        self.assertEqual(agent_input.alert["message"], "checkout-service p95 latency > 2s")
        self.assertEqual(conclusion.alert["message"], sent_alert["message"])

    def test_payment_provider_rejection_uses_a_specific_signal_id(self):
        client = fake_client(*careful_calls())
        conclusion = Agent(client, build_replay_tools(self.agent_input), "gpt-4.1-mini").run(self.agent_input.alert)
        answer = load_answer_key(CASE)
        conclusion.rejected_signals = ["payment_provider_latency"]
        self.assertTrue(grade(conclusion, answer)["gates"]["distraction"])
        conclusion.rejected_signals = ["dependency_slow"]
        self.assertFalse(grade(conclusion, answer)["gates"]["distraction"])

    def test_other_causes_need_their_own_recorded_proof(self):
        for filename, signal in (
            ("payment-dependency.json", "dependency_latency_ms"),
            ("worker-capacity.json", "worker_utilization_pct"),
        ):
            with self.subTest(case=filename):
                case = CASE.parent / filename
                check_case(case, CURRENT_SYSTEM, today=date(2026, 9, 24))
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
                self.assertTrue(grade(conclusion, answer)["passed"])
                conclusion.observations["get_metrics"][signal] = [50, 50]
                self.assertFalse(grade(conclusion, answer)["gates"]["cause"])


if __name__ == "__main__":
    unittest.main()