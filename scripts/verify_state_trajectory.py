"""Deterministic verifier for the canonical state trajectory substrate."""

from datetime import datetime, timedelta, timezone

from app.core.pipeline.contracts import DomainState, Interaction, SystemStateContract, VariableState
from app.core.state.trajectory import StateLineage, StateSnapshot, StateTrajectory


def _state(state_id: str, when: datetime, value: float, observation_id: str) -> SystemStateContract:
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
    return SystemStateContract(
        state_id=state_id,
        as_of=when,
        domains=(DomainState("system", (variable,), (observation_id,)),),
        interactions=(Interaction("load", "capacity", 0.5),),
        interaction_effects=(),
        observation_ids=(observation_id,),
        schema_version="1.0",
    )


def main() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    first = _state("s1", t0, 1.0, "o1")
    second = _state("s2", t0 + timedelta(hours=1), 2.0, "o2")
    trajectory = StateTrajectory(
        (
            StateSnapshot(first, StateLineage("s1", None, ("o1",), ("e-o1",), ("state-baseline-v1",))),
        )
    )
    transition = trajectory.append(
        StateSnapshot(second, StateLineage("s2", "s1", ("o2",), ("e-o2",), ("state-baseline-v1",)))
    )
    assert transition is not None
    assert transition.changed_variables == ("load",)
    assert transition.added_observations == ("o2",)
    assert trajectory.latest is not None and trajectory.latest.state.state_id == "s2"
    assert len(trajectory.transitions()) == 1
    print("STATE_TRAJECTORY_VERIFIER: PASS")


if __name__ == "__main__":
    main()
