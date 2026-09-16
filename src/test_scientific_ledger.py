from datetime import UTC, datetime
from pathlib import Path
import tempfile
import unittest

from mission.event_log import load_jsonl

from .scientific_execution import ScientificBoundary, build_execution_record
from .scientific_ledger import append_scientific_execution, replay_scientific_executions


def _record():
    return build_execution_record(
        execution_id="exec-1", capability_id="forecast-1", epistemic_boundary=ScientificBoundary.PREDICTIVE,
        input_ids=["x1"], source_ids=["source-1"], model_version="model-v1", data_vintage="v1",
        configuration={"horizon": 1}, parameters={"alpha": 0.1}, code_revision="abc123",
        environment="python-3.12", executed_at=datetime(2026, 9, 16, 12, tzinfo=UTC), output={"p": 0.5},
    )


class ScientificLedgerTests(unittest.TestCase):
    def test_append_replay_and_exact_retry_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scientific-events.jsonl"
            record = _record()
            first = append_scientific_execution(path, mission_id="MISSION-01", actor="INGENIERO", timestamp="2026-09-16T12:00:01Z", record=record)
            retry = append_scientific_execution(path, mission_id="MISSION-01", actor="INGENIERO", timestamp="2026-09-16T12:00:02Z", record=record)
            self.assertEqual(retry["event_id"], first["event_id"])
            self.assertEqual(len(load_jsonl(path)), 1)
            self.assertEqual(replay_scientific_executions(path), (record,))

    def test_same_execution_id_with_different_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scientific-events.jsonl"
            append_scientific_execution(path, mission_id="MISSION-01", actor="INGENIERO", timestamp="2026-09-16T12:00:01Z", record=_record())
            changed = _record().model_copy(update={"output_digest": "different"})
            with self.assertRaisesRegex(ValueError, "different scientific record"):
                append_scientific_execution(path, mission_id="MISSION-01", actor="INGENIERO", timestamp="2026-09-16T12:00:02Z", record=changed)

    def test_replay_rejects_corrupted_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scientific-events.jsonl"
            append_scientific_execution(path, mission_id="MISSION-01", actor="INGENIERO", timestamp="2026-09-16T12:00:01Z", record=_record())
            path.write_text(path.read_text(encoding="utf-8").replace("SCIENTIFIC_EXECUTION", "BROKEN"), encoding="utf-8")
            with self.assertRaises(ValueError):
                replay_scientific_executions(path)
