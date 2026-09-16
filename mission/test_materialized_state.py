import multiprocessing as mp
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .event_log import load_jsonl, validate_chain
from .materialized_state import compare_and_swap_mission, read_mission, recover_materialized_state


def _cas_worker(path: str, event_path: str, mission_id: str, expected_revision: int, projection: dict, queue, actor: str):
    try:
        result = compare_and_swap_mission(Path(path), mission_id, expected_revision, projection, event_log=Path(event_path), actor=actor, timestamp="2026-09-16T12:00:00Z")
        queue.put(("ACQUIRED", result))
    except Exception as exc:
        queue.put(("REJECTED", str(exc)))


class MaterializedStateTests(unittest.TestCase):
    def _write(self, path: Path, event_path: Path, mission_id: str = "ROMAN", revision: int = 0, status: str = "A"):
        return compare_and_swap_mission(path, mission_id, revision, {"status": status}, event_log=event_path, actor="MISSION-01", timestamp="2026-09-16T12:00:00Z")

    def test_same_mission_has_one_winner_and_one_stale_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            queue = mp.get_context("spawn").Queue()
            workers = [mp.get_context("spawn").Process(target=_cas_worker, args=(str(path), str(event_path), "ROMAN", 0, {"status": f"writer-{i}"}, queue, f"WORKER-{i}")) for i in range(2)]
            for process in workers: process.start()
            for process in workers: process.join()
            results = [queue.get() for _ in workers]
            self.assertTrue(all(process.exitcode == 0 for process in workers))
            self.assertEqual([result[0] for result in results].count("ACQUIRED"), 1)
            self.assertEqual([result[0] for result in results].count("REJECTED"), 1)
            self.assertEqual(read_mission(path, "ROMAN")["revision"], 1)
            validate_chain(load_jsonl(event_path))

    def test_event_backed_cas_persists_mutation_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            result = self._write(path, event_path)
            self.assertEqual(result["mutation_event_id"], "EV-0001")
            events = load_jsonl(event_path)
            self.assertEqual(events[0]["event_type"], "MATERIALIZED_STATE_CAS")
            self.assertEqual(events[0]["payload"]["new_revision"], 1)
            validate_chain(events)

    def test_event_backed_cas_requires_actor_and_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            with self.assertRaises(TypeError): self._call_missing(path, event_path, timestamp="2026-09-16T12:00:00Z")
            with self.assertRaises(TypeError): self._call_missing(path, event_path, actor="MISSION-01")
            with self.assertRaises(ValueError): self._write_with(path, event_path, actor="", timestamp="2026-09-16T12:00:00Z")
            with self.assertRaises(ValueError): self._write_with(path, event_path, actor="MISSION-01", timestamp="")

    def _call_missing(self, path, event_path, **kwargs):
        return compare_and_swap_mission(path, "ROMAN", 0, {}, event_log=event_path, **kwargs)

    def _write_with(self, path, event_path, *, actor, timestamp):
        return compare_and_swap_mission(path, "ROMAN", 0, {}, event_log=event_path, actor=actor, timestamp=timestamp)

    def test_independent_missions_do_not_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            self._write(path, event_path, "ROMAN", 0, "A"); self._write(path, event_path, "ESPIONA", 0, "B")
            self.assertEqual(read_mission(path, "ROMAN")["revision"], 1)
            self.assertEqual(read_mission(path, "ESPIONA")["revision"], 1)

    def test_stale_writer_is_rejected_without_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            self._write(path, event_path, "ROMAN", 0, "A")
            with self.assertRaises(ValueError): self._write(path, event_path, "ROMAN", 0, "STALE")
            self.assertEqual(read_mission(path, "ROMAN")["projection"]["status"], "A")
            self.assertEqual(len(load_jsonl(event_path)), 1)

    def test_interrupted_projection_write_is_recoverable_and_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            with patch("mission.materialized_state._atomic_write", side_effect=OSError("simulated interruption")):
                with self.assertRaises(OSError): self._write(path, event_path)
            self.assertEqual(read_mission(path, "ROMAN")["revision"], 0)
            retry = self._write(path, event_path)
            self.assertEqual(retry["revision"], 1)
            self.assertEqual(len(load_jsonl(event_path)), 1)

    def test_recovery_rejects_corrupted_event_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            self._write(path, event_path)
            event_path.write_text(event_path.read_text(encoding="utf-8").replace('"hash":"', '"hash":"x', 1), encoding="utf-8")
            with self.assertRaises(ValueError): recover_materialized_state(path, event_path)

    def test_recovery_rejects_revision_jump(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"; event_path = Path(tmp) / "events.jsonl"
            from .event_log import append_payload
            append_payload(event_path, event_type="MATERIALIZED_STATE_CAS", mission_id="ROMAN", actor="MISSION-01", timestamp="2026-09-16T12:00:00Z", payload={"expected_revision":0,"new_revision":2,"projection":{}})
            with self.assertRaises(ValueError): recover_materialized_state(path, event_path)

if __name__ == "__main__": unittest.main()
