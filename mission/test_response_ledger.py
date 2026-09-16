import tempfile
import unittest
from pathlib import Path

from .event_log import load_jsonl, validate_chain
from .response_ledger import append_response, validate_response_record


def base_record():
    return {
        "response_id":"R1","warning_presence":"PRESENT","warning_or_prediction_identity":"PRED-1",
        "decision_identity":"DEC-1","decision_time":"2026-09-16T12:00:00Z","action_identity":"ACT-1",
        "execution_time":"2026-09-16T12:10:00Z","responsible_actor":"ORG-1","response_eligibility":{"eligible":True,"window":"PT1H"},
        "intended_mechanism":"reduce declared outcome risk","response_delay":600,"intervention_exposure_intensity":{"level":1},
        "implementation_failure":None,"resource_capacity_constraints":[],"outcome_ascertainment_identity":"OUT-1",
        "response_horizon":"PT24H","counterfactual_causal_status":"INSUFFICIENT","execution_status":"EXECUTED","causal_status":"IDENTIFICATION_INSUFFICIENT"
    }

class ResponseLedgerTests(unittest.TestCase):
    def test_persists_event_backed_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/"responses.json"; events=Path(tmp)/"events.jsonl"
            result=append_response(ledger,events,base_record(),actor="MISSION-01",timestamp="2026-09-16T12:11:00Z")
            self.assertEqual(result["mutation_event_id"],"EV-0001")
            self.assertEqual(len(load_jsonl(events)),1)
            validate_chain(load_jsonl(events))

    def test_warning_without_response_is_valid(self):
        record=base_record(); record.update({"response_id":"R2","decision_identity":None,"decision_time":None,"action_identity":None,"execution_time":None,"response_delay":None,"implementation_failure":"not initiated","outcome_ascertainment_identity":None,"execution_status":"NO_RESPONSE","causal_status":"NOT_ASSESSED"})
        validate_response_record(record)

    def test_response_without_warning_is_distinct(self):
        record=base_record(); record.update({"response_id":"R3","warning_presence":"ABSENT","warning_or_prediction_identity":None})
        validate_response_record(record)

    def test_causal_support_fails_closed_without_identification(self):
        record=base_record(); record.update({"response_id":"R4","causal_status":"IDENTIFICATION_SUPPORTED","counterfactual_causal_status":"INSUFFICIENT"})
        with self.assertRaises(ValueError): validate_response_record(record)

    def test_delayed_response_requires_execution_evidence(self):
        record=base_record(); record.update({"response_id":"R5","execution_status":"DELAYED_OUTSIDE_WINDOW","execution_time":None})
        with self.assertRaises(ValueError): validate_response_record(record)

if __name__=="__main__": unittest.main()
