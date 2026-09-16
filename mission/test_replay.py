import tempfile
import unittest
from pathlib import Path
import json

from .event_log import append_payload
from .replay import replay


class ReplayTests(unittest.TestCase):
    def test_replay_reconstructs_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"events.jsonl"
            append_payload(path,event_type="CONTROL_PLANE_GENESIS",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:00:00Z",payload={})
            append_payload(path,event_type="MISSION_ADMISSION",mission_id="ROMAN",actor="MISSION-01",timestamp="2026-09-16T10:30:00Z",payload={"status":"ADMITTED_REPOSITORY_RUNTIME_PENDING","operating_standard_version":"MISSION_SYSTEM_CONSTITUTION_1.0"})
            state=replay(path)
            self.assertEqual(state.missions["ROMAN"]["status"],"ADMITTED_REPOSITORY_RUNTIME_PENDING")
            self.assertEqual(state.last_event_id,"EV-0002")

    def test_replay_rejects_unknown_event_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"events.jsonl"
            append_payload(path,event_type="CONTROL_PLANE_GENESIS",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:00:00Z",payload={})
            append_payload(path,event_type="UNSUPPORTED_EVENT",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:01:00Z",payload={})
            with self.assertRaises(ValueError): replay(path)

    def test_current_persistent_event_stream_replays_to_admitted_roman(self):
        root=Path(__file__).resolve().parents[1]
        event_path=root/"mission"/"MISSION_EVENT_LOG.jsonl"
        state_path=root/"mission"/"ROMAN_MISSION_STATE.json"
        lifecycle_path=root/"mission"/"MISSION_LIFECYCLE_LEDGER.json"
        state=replay(event_path)
        roman=json.loads(state_path.read_text(encoding="utf-8"))
        lifecycle=json.loads(lifecycle_path.read_text(encoding="utf-8"))
        self.assertEqual(state.missions["ROMAN"]["status"],roman["status"])
        self.assertEqual(state.last_event_id,"EV-0002")
        self.assertEqual(lifecycle["admissions"][0]["mutation_event_id"],state.last_event_id)

    def test_replay_normalizes_wrapped_claim_and_handoff_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"events.jsonl"
            append_payload(path,event_type="CONTROL_PLANE_GENESIS",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:00:00Z",payload={})
            append_payload(path,event_type="WORK_CLAIM_ACQUIRED",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:01:00Z",payload={"claim":{"work_id":"W1","lease_id":"L1"}})
            append_payload(path,event_type="WORK_CLAIM_RELEASED",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:02:00Z",payload={"claim":{"work_id":"W1","lease_id":"L1"}})
            append_payload(path,event_type="HANDOFF_LIFECYCLE",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:03:00Z",payload={"handoff_id":"H1","status":"ACCEPTED"})
            state=replay(path)
            self.assertEqual(state.claims["W1"]["status"],"RELEASED")
            self.assertEqual(state.handoffs["H1"]["status"],"ACCEPTED")

    def test_replay_detects_transition_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"events.jsonl"
            append_payload(path,event_type="MISSION_STATE_TRANSITION",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:00:00Z",payload={"from":"READY","to":"ACTIVE"})
            append_payload(path,event_type="MISSION_STATE_TRANSITION",mission_id="MISSION-01",actor="MISSION-01",timestamp="2026-09-16T00:01:00Z",payload={"from":"ACTIVE","to":"BLOCKED"})
            events=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            events[1]["payload"]["from"]="READY"
            broken=Path(tmp)/"broken.jsonl"
            broken.write_text("\n".join(json.dumps(event,sort_keys=True,separators=(",",":")) for event in events)+"\n",encoding="utf-8")
            with self.assertRaises(ValueError): replay(broken)


if __name__ == "__main__":
    unittest.main()
