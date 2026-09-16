import tempfile
import unittest
from pathlib import Path

from .control_plane import HandoffState
from .event_log import load_jsonl, validate_chain
from .handoff_runtime import transition


BASE={"handoff_id":"H1","source_mission":"MISSION-A","destination_mission":"MISSION-B","timestamp":"2026-09-16T12:00:00+00:00","source_commit":"abc","finding":"finding","evidence":["e0"],"affected_surface":"surface","severity":"HIGH","required_action":"execute","proposed_action":"execute","constraints":[],"dependencies":[],"validation_required":True,"acceptance_criteria":["verified"],"status":"CREATED"}


class HandoffRuntimeTests(unittest.TestCase):
    def test_full_lifecycle_is_event_backed(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry=Path(tmp)/"handoffs.json"; events=Path(tmp)/"events.jsonl"; current=dict(BASE)
            for target in (HandoffState.VALIDATION_PENDING,HandoffState.READY,HandoffState.ACCEPTED,HandoffState.IMPLEMENTING,HandoffState.IMPLEMENTED,HandoffState.VERIFIED,HandoffState.INTEGRATED):
                current=transition(registry,events,current,target_status=target,actor="SYSTEM",timestamp="2026-09-16T12:00:00+00:00",evidence=[target.value])
            self.assertEqual(current["status"],"INTEGRATED")
            self.assertEqual(current["verification_state"],"VERIFIED")
            self.assertEqual(len(load_jsonl(events)),7)
            validate_chain(load_jsonl(events))

    def test_unaccepted_handoff_cannot_jump_to_integrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry=Path(tmp)/"handoffs.json"; events=Path(tmp)/"events.jsonl"
            with self.assertRaises(ValueError):
                transition(registry,events,dict(BASE),target_status=HandoffState.INTEGRATED,actor="SYSTEM",timestamp="2026-09-16T12:00:00+00:00",evidence=["e"])


if __name__ == "__main__": unittest.main()
