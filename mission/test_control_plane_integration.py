"""Deterministic integration and multi-process control-plane validation."""
from __future__ import annotations
import json
import multiprocessing as mp
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .control_plane import MissionState
from .control_plane_runtime import persist_transition, replay_projection, replay_state
from .event_log import load_jsonl, validate_chain
from .lifecycle_governance import record_conflict
from .work_claims import acquire


def _claim_worker(root: str, work_id: str, mission_id: str, queue) -> None:
    path=Path(root)/"claims.json"; event_log=Path(root)/"events.jsonl"
    now=datetime.now(timezone.utc); expiry=(now+timedelta(minutes=5)).isoformat()
    try:
        result=acquire(path,work_id=work_id,mission_id=mission_id,actor=mission_id,lease_id=f"L-{mission_id}",lease_expires_at=expiry,event_log=event_log)
        queue.put((mission_id,"ACQUIRED",result.get("mutation_event_id")))
    except Exception as exc:
        queue.put((mission_id,"REJECTED",type(exc).__name__))


class ControlPlaneIntegrationTests(unittest.TestCase):
    def test_event_backed_state_uses_explicit_mission_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"
            event=persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.READY,target=MissionState.ACTIVE,authorized_actor="SYSTEM",evidence=["e"],timestamp="2026-09-16T12:00:00+00:00")
            self.assertEqual(event["mission_id"],"MISSION-A")
            self.assertEqual(replay_state(load_jsonl(log)),{"MISSION-A":"ACTIVE"})

    def test_two_processes_same_claim_have_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx=mp.get_context("spawn")
            queue=ctx.Queue()
            ps=[ctx.Process(target=_claim_worker,args=(tmp,"W-CONCURRENT",f"MISSION-{i}",queue)) for i in ("A","B")]
            for p in ps: p.start()
            for p in ps: p.join(15)
            self.assertTrue(all(p.exitcode==0 for p in ps), msg=[p.exitcode for p in ps])
            results=[queue.get(timeout=3) for _ in ps]
            self.assertEqual(sum(r[1]=="ACQUIRED" for r in results),1)
            self.assertEqual(sum(r[1]=="REJECTED" for r in results),1)
            events=load_jsonl(Path(tmp)/"events.jsonl")
            self.assertEqual(len(events),1)
            validate_chain(events)

    def test_event_chain_rejects_reordered_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"
            persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.READY,target=MissionState.ACTIVE,authorized_actor="SYSTEM",evidence=["e"],timestamp="2026-09-16T12:00:00+00:00")
            persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.ACTIVE,target=MissionState.VALIDATION_PENDING,authorized_actor="SYSTEM",evidence=["e2"],timestamp="2026-09-16T12:01:00+00:00")
            events=load_jsonl(log); events.reverse()
            with self.assertRaises(ValueError): validate_chain(events)

    def test_replay_projection_is_deterministic_and_detects_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"; ledger=Path(tmp)/"ledger.json"; ledger.write_text(json.dumps({"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}),encoding="utf-8")
            record_conflict(ledger,conflict_id="C1",claim_a="A",claim_b="B",category="test",owner="MISSION-A",evidence_a=["ea"],evidence_b=["eb"],event_log=log)
            events=load_jsonl(log); first=replay_projection(events); second=replay_projection(events)
            self.assertEqual(first,second); self.assertEqual(len(first["conflicts"]),1)
            events[0]["payload"]["claim_a"]="TAMPERED"
            with self.assertRaises(ValueError): validate_chain(events)

    def test_stale_transition_writer_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"events.jsonl"
            persist_transition(event_log=log,mission_id="MISSION-A",current=MissionState.READY,target=MissionState.ACTIVE,authorized_actor="SYSTEM",evidence=["e"],timestamp="2026-09-16T12:00:00+00:00")
            from .event_log import append_event, make_event
            stale=make_event(event_id="EV-STALE",event_type="MISSION_STATE_TRANSITION",mission_id="MISSION-B",actor="SYSTEM",timestamp="2026-09-16T12:00:01+00:00",payload={"from":"READY","to":"ACTIVE"})
            with self.assertRaises(ValueError): append_event(log,stale)


if __name__ == "__main__": unittest.main()
