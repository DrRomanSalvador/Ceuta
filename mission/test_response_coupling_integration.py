import tempfile
import unittest
from pathlib import Path

from src.alert_system import AlertSystem
from src.response_coupling import ResponseBinding, ResponseCouplingSink
from .event_log import load_jsonl, validate_chain
from .response_ledger import append_response


class _RiskResult:
    risk_score = 0.8
    data_sources = ["fixture"]
    audit_hash = "audit-1"
    alert_level = "ORANGE"


class ResponseCouplingMissionIntegrationTests(unittest.TestCase):
    def test_real_alert_path_can_persist_response_ledger_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "responses.json"
            events = Path(tmp) / "events.jsonl"

            def writer(**kwargs):
                return append_response(ledger, events, **kwargs)

            system = AlertSystem(response_sink=ResponseCouplingSink(writer, "MISSION-01"))
            alert = system.check_and_alert(_RiskResult())
            binding = ResponseBinding(
                response_id="RESP-REAL-PATH-1",
                prediction_identity="PRED-EXPLICIT-1",
                decision_identity="DEC-EXPLICIT-1",
                decision_time="2026-09-16T12:00:00Z",
                action_identity="ACT-EXPLICIT-1",
                execution_time="2026-09-16T12:10:00Z",
                responsible_actor="MISSION-01",
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

            result = system.record_response(
                alert, binding, actor="MISSION-01", timestamp="2026-09-16T12:11:00Z"
            )

            self.assertEqual(result["response_id"], "RESP-REAL-PATH-1")
            self.assertEqual(result["warning_or_prediction_identity"], "PRED-EXPLICIT-1")
            self.assertEqual(result["decision_identity"], "DEC-EXPLICIT-1")
            self.assertEqual(result["action_identity"], "ACT-EXPLICIT-1")
            events_data = load_jsonl(events)
            self.assertEqual(len(events_data), 1)
            self.assertEqual(events_data[0]["event_type"], "RESPONSE_COUPLING_RECORDED")
            validate_chain(events_data)


if __name__ == "__main__":
    unittest.main()
