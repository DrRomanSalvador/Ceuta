import json
import multiprocessing as mp
import tempfile
import unittest
from pathlib import Path

from .control_plane import HandoffState
from .event_log import load_jsonl, validate_chain
from .handoff_runtime import transition


BASE={"handoff_id":"H1","source_mission":"MISSION-A","destination_mission":"MISSION-B","timestamp":"2026-09-16T12:00:00+00:00","source_commit":"abc","finding":"finding","evidence":["e0"],"affected_surface":"surface","severity":"HIGH","required_action":"execute","proposed_action":"execute","constraints":[],"dependencies":[],"validation_required":True,"acceptance_criteria":["verified"],"status":"CREATED"}


def _handoff_worker(registry: str, events: str, queue) -> None:
    try:
        result=transition(
            Path(registry),
            Path(events),
            dict(BASE),
            target_status=HandoffState.VALIDATION_PENDING,
            actor="SYSTEM",
            timestamp="2026-09-16T12:00:00+00:00",
            evidence=["concurrent-worker"],
        )
        queue.put(("ACQUIRED", result["status"], result["mutation_event_id"]))
    except Exception as exc:
        queue.put(("REJECTED", type(exc).__name__, str(exc)))


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

    def test_concurrent_same_handoff_has_one_winner_and_one_stale_writer_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry=Path(tmp)/"handoffs.json"; events=Path(tmp)/"events.jsonl"
            ctx=mp.get_context("spawn")
            queue=ctx.Queue()
            processes=[ctx.Process(target=_handoff_worker,args=(str(registry),str(events),queue)) for _ in range(2)]
            for process in processes: process.start()
            for process in processes: process.join(15)
            self.assertTrue(all(process.exitcode==0 for process in processes), msg=[process.exitcode for process in processes])
            results=[queue.get(timeout=3) for _ in processes]
            self.assertEqual(sum(result[0]=="ACQUIRED" for result in results),1)
            self.assertEqual(sum(result[0]=="REJECTED" and result[1]=="ValueError" for result in results),1)
            persisted=json.loads(registry.read_text(encoding="utf-8"))
            self.assertEqual(persisted["handoffs"]["H1"]["status"],HandoffState.VALIDATION_PENDING.value)
            persisted_events=load_jsonl(events)
            self.assertEqual(len(persisted_events),1)
            validate_chain(persisted_events)


if __name__ == "__main__": unittest.main()
