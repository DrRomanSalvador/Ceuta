from backend.app.missions.autonomous_chain import (
    AutonomousChainError,
    AutonomousMissionChain,
    MissionCandidate,
    TaskCandidate,
)


def _task() -> TaskCandidate:
    return TaskCandidate(
        task_id="task-1",
        why_this_task="A validated contradiction requires a discriminative test.",
        why_now="The contradiction affects a downstream capability.",
        expected_value="MATERIAL",
        acceptance_criteria=("test result is persisted",),
        stop_condition="Contradiction resolved or evidence becomes inconclusive.",
        capability_required=("SCIENTIFIC_ADVERSARIAL",),
        source_event_refs=("event-1",),
    )


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
    bad = TaskCandidate(
        task_id="task-2",
        why_this_task="derived",
        why_now="now",
        expected_value="MATERIAL",
        acceptance_criteria=("done",),
        stop_condition="done",
        capability_required=("X",),
        source_event_refs=(),
    )
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


def test_fixed_point_requires_all_zero_conditions() -> None:
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
