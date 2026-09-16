from pathlib import Path

from app.missions.execution import Checkpoint, ExecutionTask, UniversalExecutionRuntime


def test_founder_inherits_universal_task_checkpoint_and_zero_context_recovery(tmp_path: Path):
    runtime = UniversalExecutionRuntime(tmp_path)
    task = ExecutionTask(
        task_id="FOUNDER-TASK-001", mission_id="FOUNDER", objective="Validate founder control-plane invocation",
        inputs=("docs/missions/founder/MISSION_STATE.json",), dependencies=(),
        success_criteria=("canonical discovery", "authority check", "persisted checkpoint"),
    )
    version = runtime.register_task(task)
    version = runtime.claim_task(task.task_id, expected_version=version)
    checkpoint = Checkpoint(
        checkpoint_id="FOUNDER-CP-001", mission_id="FOUNDER", mission_version="1.0.0", agent_id="ROMAN",
        execution_id="FOUNDER-EXEC-001", task_id=task.task_id, subtask="control-plane-validation", state="RUNNING",
        state_version=version, last_result="CLAIMED", last_verified_revision="test-revision",
        last_test_evidence=("founder runtime integration",), next_authorized_action="RECOVER_AND_CONTINUE",
        dependencies=(), blockers=(), delegated_tasks=(), processes=(), created_at="2026-09-16T14:00:00+00:00",
    )
    after_checkpoint = runtime.checkpoint(checkpoint, expected_version=version)
    recovered = runtime.zero_context_reconstruct(task.task_id)
    assert recovered["task"]["mission_id"] == "FOUNDER"
    assert recovered["task"]["checkpoint_ref"] == "FOUNDER-CP-001"
    assert recovered["checkpoint"]["checkpoint_id"] == "FOUNDER-CP-001"
    assert runtime.liveness(task.task_id, process_present=False, seconds_since_progress=None, observation_interval_seconds=None) == "RECOVERABLE"
    assert after_checkpoint != version


def test_founder_checkpoint_is_idempotent(tmp_path: Path):
    runtime = UniversalExecutionRuntime(tmp_path)
    task = ExecutionTask("FOUNDER-TASK-002", "FOUNDER", "checkpoint idempotence", (), (), ("checkpoint",))
    version = runtime.register_task(task)
    version = runtime.claim_task(task.task_id, expected_version=version)
    checkpoint = Checkpoint(
        checkpoint_id="FOUNDER-CP-002", mission_id="FOUNDER", mission_version="1.0.0", agent_id="ROMAN",
        execution_id="EXEC-2", task_id=task.task_id, subtask="subtask", state="RUNNING", state_version=version,
        last_result="ok", last_verified_revision="rev", last_test_evidence=("test",), next_authorized_action="CONTINUE",
        dependencies=(), blockers=(), delegated_tasks=(), processes=(), created_at="2026-09-16T14:00:00+00:00",
    )
    first = runtime.checkpoint(checkpoint, expected_version=version)
    second = runtime.checkpoint(checkpoint, expected_version=first)
    assert second == first
