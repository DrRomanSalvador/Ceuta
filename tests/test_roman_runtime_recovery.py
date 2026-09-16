from pathlib import Path

import pytest

from app.missions.registry import MissionRegistry, MissionRegistryError
from app.missions.execution import Checkpoint, ExecutionTask, UniversalExecutionRuntime

ROOT = Path(__file__).resolve().parents[1]


def test_roman_canonical_identity_and_contract_are_discoverable():
    registry = MissionRegistry(ROOT)
    mission = registry.get("ROMAN")
    contract = registry.load_contract("ROMAN")
    assert mission["mission_id"] == "ROMAN"
    assert mission["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
    assert contract["mission_id"] == "ROMAN"
    assert contract["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
    assert contract["authority"]["can_invoke"] is True
    assert contract["authority"]["can_authorize"] is False


def test_roman_canonical_invocation_enforces_authority():
    registry = MissionRegistry(ROOT)
    envelope = registry.build_invocation(
        mission_id="ROMAN", operation="AUDIT", request_id="roman-req-1", session_id="roman-session-1",
        requested_at="2026-09-16T16:00:00+02:00", authority_context={"CAN_INVOKE": True},
        input_refs=("docs/missions/roman/ROMAN_MISSION_STATE.json",), expected_output_type="RESULT", base_state_version="1",
    )
    assert envelope.mission_id == "ROMAN"
    with pytest.raises(MissionRegistryError, match="CAN_INVOKE"):
        registry.build_invocation(
            mission_id="ROMAN", operation="AUDIT", request_id="roman-req-2", session_id="roman-session-2",
            requested_at="2026-09-16T16:00:00+02:00", authority_context={"CAN_INVOKE": False},
            input_refs=(), expected_output_type="RESULT", base_state_version="1",
        )


def test_roman_universal_execution_recovery_and_idempotency(tmp_path: Path):
    runtime = UniversalExecutionRuntime(tmp_path)
    task = ExecutionTask(
        task_id="ROMAN-TASK-001", mission_id="ROMAN", objective="canonical runtime recovery",
        inputs=("docs/missions/roman/ROMAN_MISSION_STATE.json",), dependencies=(),
        success_criteria=("discovery", "authority", "checkpoint", "recovery"),
    )
    version = runtime.register_task(task)
    version = runtime.claim_task(task.task_id, expected_version=version)
    checkpoint = Checkpoint(
        checkpoint_id="ROMAN-CP-001", mission_id="ROMAN", mission_version="1.0.0", agent_id="ROMAN",
        execution_id="ROMAN-EXEC-001", task_id=task.task_id, subtask="runtime-recovery", state="RUNNING",
        state_version=version, last_result="CLAIMED", last_verified_revision="test-revision",
        last_test_evidence=("canonical ROMAN runtime",), next_authorized_action="RECOVER_AND_CONTINUE",
        dependencies=(), blockers=(), delegated_tasks=(), processes=(), created_at="2026-09-16T16:00:00+02:00",
    )
    after = runtime.checkpoint(checkpoint, expected_version=version)
    recovered = runtime.zero_context_reconstruct(task.task_id)
    assert recovered["task"]["mission_id"] == "ROMAN"
    assert recovered["task"]["checkpoint_ref"] == "ROMAN-CP-001"
    assert recovered["checkpoint"]["checkpoint_id"] == "ROMAN-CP-001"
    assert runtime.liveness(task.task_id, process_present=False, seconds_since_progress=None, observation_interval_seconds=None) == "RECOVERABLE"
    assert runtime.checkpoint(checkpoint, expected_version=after) == after


def test_universal_execution_state_must_not_claim_canonical_roman_identity():
    state = (ROOT / "docs/missions/UNIVERSAL_EXECUTION_STATE.json").read_text()
    assert '"control_id": "UNIVERSAL_EXECUTION_CONTROL"' in state
    assert '"mission_status": "COMPLETE"' in state
    # Canonical ROMAN is independently defined as AUTHORIAL_INTELLECTUAL_FORENSIC in the registry.
    registry = MissionRegistry(ROOT)
    assert registry.get("ROMAN")["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
