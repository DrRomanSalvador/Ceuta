import tempfile
import unittest
from pathlib import Path

from .control_plane import MissionState
from .control_plane_runtime import persist_handoff_event, persist_transition, replay_state
from .event_log import load_jsonl, validate_chain


class ControlPlaneRuntimeTests(unittest.TestCase):
    def test_transition_is_persisted_and_replayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            persist_transition(
                event_log=path,
                current=MissionState.READY,
                target=MissionState.ACTIVE,
                authorized_actor="MISSION-01",
                evidence=["commit:abc"],
                timestamp="2026-09-16T12:00:00Z",
            )
            events = load_jsonl(path)
            self.assertEqual(validate_chain(events), events[-1]["hash"])
            self.assertEqual(replay_state(events)["MISSION-01"], "ACTIVE")

    def test_handoff_event_preserves_lineage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            persist_handoff_event(
                event_log=path,
                mission_id="MISSION-02",
                actor="MISSION-02",
                handoff_id="H1",
                status="ACCEPTED",
                evidence=["issue-37"],
                timestamp="2026-09-16T12:00:00Z",
            )
            event = load_jsonl(path)[0]
            self.assertEqual(event["event_type"], "HANDOFF_LIFECYCLE")
            self.assertEqual(event["payload"]["handoff_id"], "H1")

    def test_replay_rejects_divergent_transition_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            persist_transition(
                event_log=path,
                current=MissionState.READY,
                target=MissionState.ACTIVE,
                authorized_actor="MISSION-01",
                evidence=["e1"],
                timestamp="2026-09-16T12:00:00Z",
            )
            persist_transition(
                event_log=path,
                current=MissionState.ACTIVE,
                target=MissionState.BLOCKED,
                authorized_actor="MISSION-01",
                evidence=["e2"],
                timestamp="2026-09-16T12:01:00Z",
            )
            events = load_jsonl(path)
            bad = dict(events[1], payload={**events[1]["payload"], "from": "READY"})
            bad["hash"] = events[1]["hash"]
            events[1] = bad
            with self.assertRaises(ValueError):
                replay_state(events)


if __name__ == "__main__":
    unittest.main()
