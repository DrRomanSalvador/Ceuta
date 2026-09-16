import json
import tempfile
import unittest
from pathlib import Path

from .control_plane import MissionState
from .event_log import load_jsonl, validate_chain
from .lifecycle_governance import record_conflict
from .replay import replay, replay_projection
from .state_machine import persist_transition


class ControlPlaneIntegrationTests(unittest.TestCase):
    def test_event_chain_rejects_reordered_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"
            persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.READY,target=MissionState.ACTIVE,authorized_actor="SYSTEM",evidence=["e"],timestamp="2026-09-16T12:00:00Z")
            persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.ACTIVE,target=MissionState.VALIDATION_PENDING,authorized_actor="SYSTEM",evidence=["e2"],timestamp="2026-09-16T12:01:00Z")
            events=load_jsonl(log); events.reverse()
            with self.assertRaises(ValueError): validate_chain(events)

    def test_replay_projection_is_deterministic_and_detects_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"; ledger=Path(tmp)/"ledger.json"; ledger.write_text(json.dumps({"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}),encoding="utf-8")
            record_conflict(ledger,conflict_id="C1",claim_a="A",claim_b="B",category="test",owner="MISSION-A",evidence_a=["ea"],evidence_b=["eb"],event_log=log,actor="MISSION-A",timestamp="2026-09-16T12:00:00Z")
            events=load_jsonl(log); first=replay_projection(events); second=replay_projection(events)
            self.assertEqual(first,second); self.assertEqual(len(first["conflicts"]),1)
            events[0]["payload"]["claim_a"]="TAMPERED"
            with self.assertRaises(ValueError): validate_chain(events)

    def test_stale_transition_writer_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"
            persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.READY,target=MissionState.ACTIVE,authorized_actor="SYSTEM",evidence=["e"],timestamp="2026-09-16T12:00:00Z")
            from .event_log import append_event, make_event
            stale=make_event(event_id="EV-STALE",event_type="MISSION_STATE_TRANSITION",mission_id="MISSION-B",actor="SYSTEM",timestamp="2026-09-16T12:00:01Z",payload={"from":"READY","to":"ACTIVE"})
            with self.assertRaises(ValueError): append_event(log,stale)

if __name__=="__main__": unittest.main()
