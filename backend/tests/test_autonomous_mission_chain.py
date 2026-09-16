from dataclasses import replace
import subprocess
import sys

from backend.app.missions.autonomous_chain import (
    AutonomousChainError,
    AutonomousMissionChain,
    FixedPointState,
    MissionCandidate,
    ProcessObservation,
    ScientificWorkEvent,
    TaskCandidate,
    WorkQueue,
)


def _task(task_id: str = "task-1") -> TaskCandidate:
    return TaskCandidate(
        task_id=task_id,
        why_this_task="A validated contradiction requires a discriminative test.",
        why_now="The contradiction affects a downstream capability.",
        expected_value="MATERIAL",
        acceptance_criteria=("test result is persisted",),
        stop_condition="Contradiction resolved or evidence becomes inconclusive.",
        capability_required=("SCIENTIFIC_ADVERSARIAL",),
        source_event_refs=("event-1",),
    )


def test_scientific_work_event_is_provenance_gated() -> None:
    event = ScientificWorkEvent(
        event_id="event-1",
        event_type="SCIENTIFIC_CONSEQUENCE",
        source_refs=("result-1",),
        scientific_reason="A result changes the downstream validation obligation.",
        affected_refs=("claim-1",),
        capability_implications=("SCIENTIFIC_ADVERSARIAL",),
        validation_status="VALIDATED",
        provenance_refs=("prov-1",),
        state_version="state-1",
        emitted_at="2026-09-16T11:00:00Z",
    )
    assert AutonomousMissionChain.emit_scientific_event(event) == event


def test_scientific_work_event_without_provenance_fails_closed() -> None:
    event = ScientificWorkEvent(
        event_id="event-2",
        event_type="SCIENTIFIC_CONSEQUENCE",
        source_refs=("result-2",),
        scientific_reason="derived",
        affected_refs=(),
        capability_implications=(),
        validation_status="VALIDATED",
        provenance_refs=(),
        state_version="state-1",
        emitted_at="2026-09-16T11:00:00Z",
    )
    try:
        AutonomousMissionChain.emit_scientific_event(event)
    except AutonomousChainError as exc:
        assert "SCIENTIFIC_EVENT_INVALID" in str(exc)
    else:
        raise AssertionError("scientific trigger without provenance must fail")


def test_existing_capability_selection_is_deterministic() -> None:
    task = _task()
    candidates = (
        MissionCandidate("MISSION-B", True, True, True, True, True, True, 9, 4, 1, 0),
        MissionCandidate("MISSION-A", True, True, True, True, True, True, 9, 4, 1, 0),
    )
    decision = AutonomousMissionChain.select_existing(task, candidates)
    assert decision.selected_mission == "MISSION-A"
    assert decision.precedence == "EXISTING_CAPABILITY"


def test_extension_is_used_only_when_no_direct_capability_exists() -> None:
    task = _task()
    candidates = (
        MissionCandidate("MISSION-EXT", True, True, True, True, True, True, 10, 1, 0, 0, can_extend=True),
    )
    decision = AutonomousMissionChain.select_existing(task, candidates)
    assert decision.selected_mission == "MISSION-EXT"
    assert decision.precedence == "EXISTING_MISSION_EXTENSION"


def test_no_existing_capability_does_not_invent_a_mission() -> None:
    task = _task()
    candidate = MissionCandidate("MISSION-X", False, True, True, True, True, True, 10, 1, 0, 0)
    decision = AutonomousMissionChain.select_existing(task, (candidate,))
    assert decision.selected_mission is None
    assert decision.precedence == "NO_EXISTING_CAPABILITY"


def test_material_modification_requires_revalidation() -> None:
    try:
        AutonomousMissionChain.consequence(
            consequence_id="c-1",
            source_result_refs=("result-1",),
            classification="MODIFIES",
            downstream_task_refs=(),
            revalidation_refs=(),
            material=True,
        )
    except AutonomousChainError as exc:
        assert "REVALIDATION" in str(exc)
    else:
        raise AssertionError("material modification without revalidation must fail closed")


def test_generated_result_never_counts_as_provenance_free_activation() -> None:
    bad = _task("task-2")
    bad = replace(bad, source_event_refs=())
    try:
        AutonomousMissionChain.validate_task(bad)
    except AutonomousChainError as exc:
        assert "TASK_CONTRACT_INVALID" in str(exc)
    else:
        raise AssertionError("task without source event provenance must fail")


def test_circuit_breaker_fails_closed_on_provenance_or_authority_loss() -> None:
    assert AutonomousMissionChain.circuit_break("provenance", provenance_ok=False)
    assert AutonomousMissionChain.circuit_break("authority", authority_ok=False)
    assert AutonomousMissionChain.circuit_break("recursion", recursion_depth=8)
    assert not AutonomousMissionChain.circuit_break("normal", recursion_depth=1, task_count=2)


def test_running_process_is_active_and_requires_reobservation() -> None:
    process = ProcessObservation(
        process_id="ci-672",
        process_type="CI",
        started_at="2026-09-16T11:00:00Z",
        current_status="RUNNING",
        last_observed_at="2026-09-16T11:05:00Z",
        expected_result="workflow conclusion",
        dependencies=("commit-1",),
        dependent_tasks=("post-ci-reaudit",),
        independent_tasks_available=("architecture-audit",),
        next_observation_condition="workflow conclusion or failure",
    )
    assert AutonomousMissionChain.observe_process(process).current_status == "RUNNING"


def test_work_queue_never_treats_running_as_waiting() -> None:
    queue = WorkQueue(running=("ci-672",), executable_now=())
    assert AutonomousMissionChain.queue_state(queue) == "ACTIVE"
    assert not queue.waiting_is_valid


def test_work_queue_rejects_duplicate_work_items() -> None:
    queue = WorkQueue(running=("ci-672",), delegated=("ci-672",))
    try:
        queue.validate()
    except AutonomousChainError as exc:
        assert "WORK_QUEUE_DUPLICATE" in str(exc)
    else:
        raise AssertionError("a work item cannot occupy two queue states")


def test_zero_context_replay_is_deterministic() -> None:
    task_a = _task("task-a")
    task_b = _task("task-b")
    candidates = {
        "task-a": (
            MissionCandidate("MISSION-B", True, True, True, True, True, True, 5, 1, 0, 0),
            MissionCandidate("MISSION-A", True, True, True, True, True, True, 5, 1, 0, 0),
        ),
        "task-b": (
            MissionCandidate("MISSION-C", True, True, True, True, True, True, 6, 2, 0, 0),
        ),
    }
    first = AutonomousMissionChain.replay_selection_trace((task_a, task_b), candidates)
    second = AutonomousMissionChain.replay_selection_trace((task_a, task_b), candidates)
    assert first == second
    assert tuple(decision.selected_mission for decision in first) == ("MISSION-A", "MISSION-C")


def test_replay_rejects_duplicate_task_identity() -> None:
    task = _task("duplicate")
    try:
        AutonomousMissionChain.replay_selection_trace((task, task), {})
    except AutonomousChainError as exc:
        assert "REPLAY_DUPLICATE_TASK" in str(exc)
    else:
        raise AssertionError("replay must reject duplicate task identity")


def test_isolated_subprocess_can_reconstruct_core_policy_without_live_state() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from backend.app.missions.autonomous_chain import AutonomousMissionChain; "
            "assert AutonomousMissionChain.circuit_break('isolated', recursion_depth=8)",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_full_fixed_point_includes_processes_contradictions_and_discovery() -> None:
    closed = FixedPointState(
        executable_open_work=0,
        unprocessed_derived_work=0,
        unintegrated_completed_work=0,
        unreconciled_state=0,
        unverified_internal_repair=0,
        untested_executable_change=0,
        unfollowed_active_handoff=0,
    )
    assert AutonomousMissionChain.fixed_point_state(closed)
    assert not AutonomousMissionChain.fixed_point_state(replace(closed, active_internal_processes=1))
    assert not AutonomousMissionChain.fixed_point_state(replace(closed, unresolved_critical_contradictions=1))
    assert not AutonomousMissionChain.fixed_point_state(replace(closed, unprocessed_high_value_discovery=1))


def test_fixed_point_legacy_arguments_remain_compatible() -> None:
    assert AutonomousMissionChain.fixed_point(
        executable_open_work=0,
        unprocessed_derived_work=0,
        unintegrated_completed_work=0,
        unreconciled_state=0,
        unverified_internal_repair=0,
        untested_executable_change=0,
        unfollowed_active_handoff=0,
    )
    assert not AutonomousMissionChain.fixed_point(
        executable_open_work=1,
        unprocessed_derived_work=0,
        unintegrated_completed_work=0,
        unreconciled_state=0,
        unverified_internal_repair=0,
        untested_executable_change=0,
        unfollowed_active_handoff=0,
    )
