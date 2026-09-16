from datetime import UTC, datetime

from src.scientific_execution import ScientificBoundary, build_execution_record
from src.scientific_ledger import append_scientific_execution
from mission.replay import replay


def test_scientific_execution_replays_into_control_plane_state(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    record = build_execution_record(
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
    append_scientific_execution(
        path,
        mission_id="MISSION-01",
        actor="INGENIERO",
        timestamp="2026-09-16T12:00:01Z",
        record=record,
    )
    state = replay(path)
    assert state.scientific_executions["exec-1"]["capability_id"] == "forecast-1"
    assert state.scientific_executions["exec-1"]["event_id"] == "EV-0001"
