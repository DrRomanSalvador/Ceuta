import json
import unittest
from pathlib import Path

from .invocation_runtime import authorize_invocation, compare_and_swap, discover, fresh_chat_discovery, validate_request, validate_response


class InvocationRuntimeTests(unittest.TestCase):
    def registry(self):
        return {"missions":[{"mission_id":"ROMAN","canonical_name":"ROMÁN","current_status":"REGISTERED_SOURCE_REQUIRES_ADMISSION","invocation_contract":"docs/missions/roman/ROMAN_INVOCATION_CONTRACT.json","bootstrap":"docs/missions/roman/ROMAN_BOOTSTRAP.md"}]}

    def request(self):
        return {"mission_id":"ROMAN","operation":"DISCOVER","request_id":"R1","session_id":"S1","requested_at":"2026-09-16T10:00:00Z","authority_context":{"CAN_INVOKE":True,"CAN_READ":True},"input_refs":[],"expected_output_type":"DISCOVERY","base_state_version":"v1"}

    def test_current_branch_registry_discovers_roman(self):
        root=Path(__file__).resolve().parent
        registry=json.loads((root/"MISSION_REGISTRY.json").read_text(encoding="utf-8"))
        mission=discover(registry,mission_id="ROMAN")
        self.assertEqual(mission["current_status"],"ADMITTED_REPOSITORY_RUNTIME_PENDING")
        self.assertEqual(mission["invocation_contract"],"mission/ROMAN_INVOCATION_CONTRACT.json")
        self.assertTrue((root/"ROMAN_INVOCATION_CONTRACT.json").exists())
        self.assertTrue((root/"ROMAN_MISSION_STATE.json").exists())

    def test_zero_context_discovery_is_read_only_and_identity_bound(self):
        result=fresh_chat_discovery(self.registry(),"ROMAN")
        self.assertTrue(result["discovered"])
        self.assertEqual(result["mission_id"],"ROMAN")

    def test_invocation_envelope_requires_all_fields(self):
        envelope=validate_request(self.request())
        self.assertEqual(envelope.request_id,"R1")
        with self.assertRaises(ValueError):
            validate_request({"mission_id":"ROMAN"})

    def test_invocation_requires_authority_separately(self):
        mission=self.registry()["missions"][0]
        authorize_invocation(mission=mission,envelope=validate_request(self.request()))
        request=self.request(); request["authority_context"]={"CAN_READ":True}
        with self.assertRaises(PermissionError):
            authorize_invocation(mission=mission,envelope=validate_request(request))

    def test_stale_writer_fails_closed(self):
        with self.assertRaises(RuntimeError):
            compare_and_swap(current_state_version="v2",base_state_version="v1",state_delta={"x":1})
        self.assertEqual(compare_and_swap(current_state_version="v1",base_state_version="v1",state_delta={"x":1}),"CAS_ACCEPTED")

    def test_successful_response_requires_delta_or_explicit_no_delta(self):
        response={"mission_id":"ROMAN","request_id":"R1","operation":"DISCOVER","status":"SUCCESS","result_refs":[],"source_refs":["registry"],"evidence_level":2,"state_version_read":"v1","state_delta_ref":"NO_PERSISTENCE_DELTA","handoff_refs":[],"conflict_status":"NONE","next_authorized_action":"CONTINUE"}
        validate_response(response)
        response["state_delta_ref"]=""
        with self.assertRaises(ValueError):
            validate_response(response)


if __name__ == "__main__":
    unittest.main()
