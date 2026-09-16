import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
