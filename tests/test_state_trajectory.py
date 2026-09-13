from datetime import datetime, timedelta, timezone

import pytest

from app.core.errors import ContractViolation, TemporalViolation
from app.core.pipeline.contracts import (
    DomainState,
    Interaction,
    SystemStateContract,
    VariableState,
)
from app.core.state.trajectory import (
    StateLineage,
    StateSnapshot,
    StateTrajectory,
    StateUncertainty,
)


UTC = timezone.utc


def make_state(state_id: str, when: datetime, value: float, observation_id: str) -> SystemStateContract:
    variable = VariableState(
        variable="load",
        value=value,
        previous_value=None,
        velocity=None,
        acceleration=None,
        observations=1,
        updated_at=when,
        evidence_ids=(f"e-{observation_id}",),
    )
    domain = DomainState(
        domain="system",
        variables=(variable,),
        observation_ids=(observation_id,),
    )
    return SystemStateContract(
        state_id=state_id,
        as_of=when,
        domains=(domain,),
        interactions=(Interaction("load", "capacity", 0.5),),
        interaction_effects=(),
        observation_ids=(observation_id,),
        schema_version="1.0",
    )


def snapshot(state: SystemStateContract, parent: str | None) -> StateSnapshot:
    return StateSnapshot(
        state=state,
        lineage=StateLineage(
            state_id=state.state_id,
            parent_state_id=parent,
            observation_ids=state.observation_ids,
            evidence_ids=(f"e-{state.observation_ids[0]}",),
            model_ids=("state-baseline-v1",),
        ),
        uncertainties=(StateUncertainty("load", 0.2, "epistemic", "synthetic test"),),
    )


def test_trajectory_is_append_only_and_exposes_transition() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    first = snapshot(make_state("s1", t0, 1.0, "o1"), None)
    second = snapshot(make_state("s2", t0 + timedelta(hours=1), 2.0, "o2"), "s1")

    trajectory = StateTrajectory()
    assert trajectory.append(first) is None
    transition = trajectory.append(second)

    assert transition is not None
    assert transition.from_state_id == "s1"
    assert transition.to_state_id == "s2"
    assert transition.added_observations == ("o2",)
    assert transition.changed_variables == ("load",)
    assert trajectory.latest == second
    assert len(trajectory.transitions()) == 1


def test_trajectory_rejects_time_reversal() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    trajectory = StateTrajectory([snapshot(make_state("s1", t0, 1.0, "o1"), None)])
    earlier = snapshot(make_state("s2", t0 - timedelta(seconds=1), 2.0, "o2"), "s1")

    with pytest.raises(TemporalViolation):
        trajectory.append(earlier)


def test_trajectory_requires_lineage_to_follow_previous_state() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    trajectory = StateTrajectory([snapshot(make_state("s1", t0, 1.0, "o1"), None)])
    orphan = snapshot(make_state("s2", t0 + timedelta(hours=1), 2.0, "o2"), "other")

    with pytest.raises(ContractViolation):
        trajectory.append(orphan)


def test_uncertainty_preserves_kind_and_basis() -> None:
    uncertainty = StateUncertainty("load", 0.25, "aleatoric", "measurement dispersion")
    assert uncertainty.kind == "aleatoric"
    assert uncertainty.basis == "measurement dispersion"
