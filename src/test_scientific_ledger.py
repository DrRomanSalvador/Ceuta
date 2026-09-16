from datetime import UTC, datetime

import pytest

from mission.event_log import load_jsonl

from .scientific_execution import ScientificBoundary, build_execution_record
from .scientific_ledger import append_scientific_execution, replay_scientific_executions


def _record():
    return build_execution_record(
        execution_id="exec-1",
        capability_id="forecast-1",
        epistemic_boundary=ScientificBoundary.PREDICTIVE,
        input_ids=["x1"],
        source_ids=["source-1"],
        model_version="model-v1",
        data_vintage="v1",
        configuration={"horizon": 1},
        parameters={"alpha": 0.1},
        code_revision="abc123",
        environment="python-3.12",
        executed_at=datetime(2026, 9, 16, 12, tzinfo=UTC),
        output={"p": 0.5},
    )


def test_append_replay_and_exact_retry_are_idempotent(tmp_path) -> None:
    path = tmp_path / "scientific-events.jsonl"
    record = _record()
    first = append_scientific_execution(
        path,
        mission_id="MISSION-01",
        actor="INGENIERO",
        timestamp="2026-09-16T12:00:01Z",
        record=record,
    )
    retry = append_scientific_execution(
        path,
        mission_id="MISSION-01",
        actor="INGENIERO",
        timestamp="2026-09-16T12:00:02Z",
        record=record,
    )
    assert retry["event_id"] == first["event_id"]
    assert len(load_jsonl(path)) == 1
    assert replay_scientific_executions(path) == (record,)


def test_same_execution_id_with_different_record_is_rejected(tmp_path) -> None:
    path = tmp_path / "scientific-events.jsonl"
    append_scientific_execution(
        path,
        mission_id="MISSION-01",
        actor="INGENIERO",
        timestamp="2026-09-16T12:00:01Z",
        record=_record(),
    )
    changed = _record().model_copy(update={"output_digest": "different"})
    with pytest.raises(ValueError, match="different scientific record"):
        append_scientific_execution(
            path,
            mission_id="MISSION-01",
            actor="INGENIERO",
            timestamp="2026-09-16T12:00:02Z",
            record=changed,
        )


def test_replay_rejects_corrupted_chain(tmp_path) -> None:
    path = tmp_path / "scientific-events.jsonl"
    append_scientific_execution(
        path,
        mission_id="MISSION-01",
        actor="INGENIERO",
        timestamp="2026-09-16T12:00:01Z",
        record=_record(),
    )
    path.write_text(path.read_text(encoding="utf-8").replace("SCIENTIFIC_EXECUTION", "BROKEN"), encoding="utf-8")
    with pytest.raises(ValueError):
        replay_scientific_executions(path)
