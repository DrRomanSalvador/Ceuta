import unittest

from .alert_system import AlertSystem
from .response_coupling import ResponseBinding, ResponseCouplingSink


class _RiskResult:
    risk_score = 0.8
    data_sources = ["fixture"]
    audit_hash = "audit-1"
    alert_level = "ORANGE"


def _binding(**overrides):
    values = dict(
        response_id="RESP-1",
        prediction_identity="PRED-1",
        decision_identity="DEC-1",
        decision_time="2026-09-16T12:00:00Z",
        action_identity="ACT-1",
        execution_time="2026-09-16T12:10:00Z",
        responsible_actor="ORG-1",
        response_eligibility={"eligible": True, "window": "PT1H"},
        intended_mechanism="declared mechanism",
        response_delay=600,
        intervention_exposure_intensity={"level": 1},
        implementation_failure=None,
        resource_capacity_constraints=[],
        outcome_ascertainment_identity=None,
        response_horizon="PT24H",
        counterfactual_causal_status="INSUFFICIENT",
        execution_status="EXECUTED",
        causal_status="IDENTIFICATION_INSUFFICIENT",
    )
    values.update(overrides)
    return ResponseBinding(**values)


class ResponseCouplingIntegrationTests(unittest.TestCase):
    def test_alert_can_bind_only_explicit_response_identities(self):
        captured = []
        def writer(**kwargs):
            captured.append(kwargs)
            return kwargs["record"]
        sink = ResponseCouplingSink(writer, mission_id="MISSION-01")
        system = AlertSystem(response_sink=sink)
        alert = system.check_and_alert(_RiskResult())
        record = system.record_response(alert, _binding(), actor="ORG-1", timestamp="2026-09-16T12:11:00Z")
        self.assertEqual(record["warning_or_prediction_identity"], "PRED-1")
        self.assertEqual(record["decision_identity"], "DEC-1")
        self.assertEqual(record["action_identity"], "ACT-1")
        self.assertEqual(record["warning_audit_hash"], "audit-1")
        self.assertEqual(len(captured), 1)

    def test_audit_hash_is_not_used_as_prediction_identity(self):
        sink = ResponseCouplingSink(lambda **kwargs: kwargs["record"], "MISSION-01")
        system = AlertSystem(response_sink=sink)
        alert = system.check_and_alert(_RiskResult())
        record = system.record_response(alert, _binding(
            response_id="RESP-2", prediction_identity="PRED-2", decision_identity=None,
            decision_time=None, action_identity=None, execution_time=None,
            responsible_actor="ORG-1", response_eligibility={"eligible": True},
            intended_mechanism=None, response_delay=None,
            intervention_exposure_intensity=None, implementation_failure="not initiated",
            response_horizon=None, counterfactual_causal_status="ABSENT",
            execution_status="NO_RESPONSE", causal_status="NOT_ASSESSED"
        ), actor="ORG-1", timestamp="2026-09-16T12:11:00Z")
        self.assertEqual(record["warning_or_prediction_identity"], "PRED-2")
        self.assertEqual(record["warning_audit_hash"], "audit-1")
        self.assertNotEqual(record["warning_or_prediction_identity"], record["warning_audit_hash"])

    def test_missing_sink_fails_closed(self):
        system = AlertSystem()
        alert = system.check_and_alert(_RiskResult())
        with self.assertRaises(RuntimeError):
            system.record_response(alert, _binding(), actor="ORG-1", timestamp="2026-09-16T12:11:00Z")

    def test_executed_response_requires_action_identity(self):
        with self.assertRaises(ValueError):
            _binding(action_identity=None, execution_time=None).validate()

    def test_unknown_execution_status_fails_closed(self):
        with self.assertRaises(ValueError):
            _binding(execution_status="DECIDED", decision_identity=None, decision_time=None).validate()

    def test_delayed_response_requires_delay(self):
        with self.assertRaises(ValueError):
            _binding(execution_status="DELAYED_OUTSIDE_WINDOW", response_delay=None).validate()

    def test_actor_mismatch_fails_closed(self):
        sink = ResponseCouplingSink(lambda **kwargs: kwargs["record"], "MISSION-01")
        system = AlertSystem(response_sink=sink)
        alert = system.check_and_alert(_RiskResult())
        with self.assertRaises(ValueError):
            system.record_response(alert, _binding(), actor="OTHER-ORG", timestamp="2026-09-16T12:11:00Z")


if __name__ == "__main__":
    unittest.main()
