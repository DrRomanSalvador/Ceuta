from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.missions.execution import (
    Checkpoint,
    ExecutionControlError,
    ExecutionTask,
    UniversalExecutionRuntime,
)
from backend.app.missions.registry import MissionRegistry


ROOT = Path(__file__).resolve().parents[1]


def _task(task_id: str = "T-1") -> ExecutionTask:
    return ExecutionTask(
        task_id=task_id,
        mission_id="TEST-MISSION",
        objective="material test unit",
        inputs=("input:1",),
        dependencies=(),
        success_criteria=("result exists",),
        created_at="2026-09-16T00:00:00+00:00",
        updated_at="2026-09-16T00:00:00+00:00",
        next_action="EXECUTE",
    )


def _checkpoint(state_version: str, checkpoint_id: str = "CP-1") -> Checkpoint:
    return Checkpoint(
        checkpoint_id=checkpoint_id,
        mission_id="TEST-MISSION",
        mission_version="1",
        agent_id="TEST",
        execution_id="E-1",
        task_id="T-1",
        subtask="unit",
        state="RUNNING",
        state_version=state_version,
        last_result="result:1",
        last_verified_revision="rev:1",
        last_test_evidence=("test:1",),
        next_authorized_action="RESUME",
        dependencies=(),
        blockers=(),
        delegated_tasks=(),
        processes=(),
        created_at="2026-09-16T00:00:00+00:00",
    )


def _checks() -> dict[str, bool]:
    return {
        "contradiction": True,
        "duplication": True,
        "complexity": True,
        "degradation": True,
        "regression": True,
        "integration": True,
        "maintainability": True,
        "security": True,
        "persistence": True,
    }


def test_pre_and_post_write_gates_are_distinct_and_fail_closed() -> None:
    pre = UniversalExecutionRuntime.pre_write_coherence_gate(checks=_checks(), evidence_refs=("e:1",))
    assert pre.passed
    post = UniversalExecutionRuntime.post_write_coherence_gate(checks=_checks(), evidence_refs=("e:1",), tests_passed=False, persisted=True)
    assert not post.passed
    assert "TESTS_FAILED" in post.failures


def test_task_checkpoint_recovery_and_cas(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    version = runtime.current_version()
    version = runtime.register_task(_task(), expected_version=version)
    version = runtime.claim_task("T-1", expected_version=version)
    checkpoint = _checkpoint(version)
    version_after_checkpoint = runtime.checkpoint(checkpoint, expected_version=version)

    persisted = runtime.load()
    assert persisted["tasks"]["T-1"]["checkpoint_ref"] == "CP-1"
    assert persisted["checkpoints"]["CP-1"]["payload"]["task_id"] == "T-1"
    assert runtime.recover_checkpoint("T-1").checkpoint_id == "CP-1"

    assert runtime.checkpoint(checkpoint, expected_version=version_after_checkpoint) == version_after_checkpoint
    with pytest.raises(ExecutionControlError, match="STALE_STATE_VERSION"):
        runtime.claim_task("T-1", expected_version=version)

    restarted = UniversalExecutionRuntime(tmp_path)
    reconstructed = restarted.zero_context_reconstruct("T-1")
    assert reconstructed["task"]["checkpoint_ref"] == "CP-1"
    assert reconstructed["checkpoint"]["checkpoint_id"] == "CP-1"
    assert restarted.liveness("T-1", process_present=False, seconds_since_progress=None, observation_interval_seconds=None) == "RECOVERABLE"


def test_checkpoint_reference_must_survive_process_loss(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    version = runtime.register_task(_task())
    version = runtime.claim_task("T-1", expected_version=version)
    runtime.checkpoint(_checkpoint(version), expected_version=version)
    simulated_new_process = UniversalExecutionRuntime(tmp_path)
    assert simulated_new_process.liveness("T-1", process_present=False, seconds_since_progress=None, observation_interval_seconds=None) == "RECOVERABLE"
    assert simulated_new_process.recover_checkpoint("T-1").last_result == "result:1"


def test_post_write_gate_blocks_completion(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    version = runtime.register_task(_task())
    version = runtime.claim_task("T-1", expected_version=version)
    failed = UniversalExecutionRuntime.post_write_coherence_gate(checks=_checks(), evidence_refs=("e:1",), tests_passed=True, persisted=False)
    with pytest.raises(ExecutionControlError, match="POST_WRITE_COHERENCE_GATE_FAILED"):
        runtime.complete_task("T-1", post_write_gate=failed, result_ref="r:1", evidence_refs=("e:1",), checkpoint_ref="CP-1", expected_version=version)


def test_continuation_distinguishes_work_waiting_and_completion_candidate(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    assert runtime.decide_continuation() == "MISSION_COMPLETE_CANDIDATE"
    version = runtime.register_task(_task())
    assert runtime.decide_continuation() == "CONTINUE"
    runtime.mark_blocked("T-1", external=True, reason="external dependency", expected_version=version)
    assert runtime.decide_continuation() == "WAIT"


def test_waiting_is_not_done_and_internal_work_prevents_fixed_point(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    version = runtime.register_task(_task())
    runtime.mark_blocked("T-1", external=True, reason="external dependency", expected_version=version)
    assert runtime.decide_continuation() == "WAIT"
    assert not runtime.fixed_point()


def test_liveness_does_not_equate_silence_with_failure(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    runtime.register_task(_task())
    assert runtime.liveness("T-1", process_present=True, seconds_since_progress=None, observation_interval_seconds=None) == "ACTIVE"
    assert runtime.liveness("T-1", process_present=True, seconds_since_progress=5, observation_interval_seconds=10) == "ACTIVE"
    assert runtime.liveness("T-1", process_present=True, seconds_since_progress=11, observation_interval_seconds=10) == "STALLED"
    assert runtime.liveness("T-1", process_present=None, seconds_since_progress=None, observation_interval_seconds=None) == "UNKNOWN"
    assert runtime.liveness("T-1", process_present=False, seconds_since_progress=None, observation_interval_seconds=None) == "LOST"


def test_fixed_point_can_close_at_internal_boundary(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    assert runtime.fixed_point()


def test_registry_exposes_universal_inheritance() -> None:
    registry = MissionRegistry(ROOT)
    contract = registry.load_contract("ROMAN")
    assert contract["execution_inheritance"] == "MANDATORY"
    assert contract["universal_execution_contract"]["contract_id"] == "UNIVERSAL_EXECUTION_CONTROL"


def test_fixed_point_does_not_depend_on_external_protection(tmp_path: Path) -> None:
    runtime = UniversalExecutionRuntime(tmp_path)
    state = runtime.load()
    assert state["fixed_point_requirements"]["external_protection_verified"] is False
    assert state["fixed_point_requirements"]["cross_process_verified"] is False
    assert runtime.fixed_point() is True
