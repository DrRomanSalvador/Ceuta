"""Canonical, auditable trajectory semantics for CeutIA.

A trajectory is an ordered sequence of immutable system-state snapshots. It is
not a forecast and it does not imply causality. The purpose of this module is
to make temporal state, lineage, transitions, and uncertainty explicit and
reproducible before downstream forecasting or decision logic consumes them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable

from ..errors import ContractViolation, TemporalViolation
from ..pipeline.contracts import SystemStateContract


@dataclass(frozen=True, slots=True)
class StateUncertainty:
    """Uncertainty attached to a state component without collapsing its type."""

    component: str
    value: float
    kind: str
    basis: str

    def __post_init__(self) -> None:
        if not self.component or not self.kind or not self.basis:
            raise ContractViolation("uncertainty component, kind and basis are required")
        if not isfinite(float(self.value)) or self.value < 0.0:
            raise ContractViolation("uncertainty value must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class StateLineage:
    """Reproducibility metadata for one state snapshot."""

    state_id: str
    parent_state_id: str | None
    observation_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    model_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.state_id:
            raise ContractViolation("state_id must not be empty")
        if self.parent_state_id == self.state_id:
            raise ContractViolation("state cannot be its own parent")
        if any(not value for value in self.observation_ids):
            raise ContractViolation("observation_ids must not contain empty values")
        if any(not value for value in self.evidence_ids):
            raise ContractViolation("evidence_ids must not contain empty values")
        if any(not value for value in self.model_ids):
            raise ContractViolation("model_ids must not contain empty values")


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """State plus the metadata required to interpret it scientifically."""

    state: SystemStateContract
    lineage: StateLineage
    uncertainties: tuple[StateUncertainty, ...] = ()

    def __post_init__(self) -> None:
        if self.lineage.state_id != self.state.state_id:
            raise ContractViolation("lineage state_id must match state.state_id")
        state_observations = set(self.state.observation_ids)
        if not set(self.lineage.observation_ids).issubset(state_observations):
            raise ContractViolation("lineage observations must belong to the state")


@dataclass(frozen=True, slots=True)
class StateTransition:
    """Observed transition between two consecutive states."""

    from_state_id: str
    to_state_id: str
    from_time: datetime
    to_time: datetime
    added_observations: tuple[str, ...]
    changed_variables: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.from_state_id or not self.to_state_id:
            raise ContractViolation("transition state ids are required")
        if self.from_state_id == self.to_state_id:
            raise ContractViolation("transition endpoints must differ")
        for name, value in (("from_time", self.from_time), ("to_time", self.to_time)):
            if value.tzinfo is None or value.utcoffset() is None:
                raise TemporalViolation(f"{name} must be timezone-aware")
        if self.to_time <= self.from_time:
            raise TemporalViolation("state transitions must move forward in time")
        if any(not value for value in self.added_observations):
            raise ContractViolation("added_observations must not contain empty values")
        if any(not value for value in self.changed_variables):
            raise ContractViolation("changed_variables must not contain empty values")


class StateTrajectory:
    """Append-only temporal history of state snapshots.

    The trajectory rejects time reversal and duplicate state identifiers. It
    exposes transitions only between adjacent snapshots; no causal meaning is
    assigned to a transition.
    """

    def __init__(self, snapshots: Iterable[StateSnapshot] = ()) -> None:
        self._snapshots: list[StateSnapshot] = []
        for snapshot in snapshots:
            self.append(snapshot)

    def append(self, snapshot: StateSnapshot) -> StateTransition | None:
        if any(existing.state.state_id == snapshot.state.state_id for existing in self._snapshots):
            raise ContractViolation("state_id already exists in trajectory")
        if not self._snapshots:
            self._snapshots.append(snapshot)
            return None

        previous = self._snapshots[-1]
        if snapshot.state.as_of <= previous.state.as_of:
            raise TemporalViolation("trajectory state times must be strictly increasing")
        if snapshot.lineage.parent_state_id != previous.state.state_id:
            raise ContractViolation("snapshot parent_state_id must reference the previous state")

        previous_variables = {
            item.variable: item.value
            for domain in previous.state.domains
            for item in domain.variables
        }
        current_variables = {
            item.variable: item.value
            for domain in snapshot.state.domains
            for item in domain.variables
        }
        changed = tuple(
            sorted(
                name
                for name in set(previous_variables) | set(current_variables)
                if previous_variables.get(name) != current_variables.get(name)
            )
        )
        added = tuple(
            item
            for item in snapshot.state.observation_ids
            if item not in set(previous.state.observation_ids)
        )
        transition = StateTransition(
            from_state_id=previous.state.state_id,
            to_state_id=snapshot.state.state_id,
            from_time=previous.state.as_of,
            to_time=snapshot.state.as_of,
            added_observations=added,
            changed_variables=changed,
        )
        self._snapshots.append(snapshot)
        return transition

    @property
    def snapshots(self) -> tuple[StateSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def latest(self) -> StateSnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def transitions(self) -> tuple[StateTransition, ...]:
        result: list[StateTransition] = []
        for previous, current in zip(self._snapshots, self._snapshots[1:]):
            result.append(
                StateTransition(
                    from_state_id=previous.state.state_id,
                    to_state_id=current.state.state_id,
                    from_time=previous.state.as_of,
                    to_time=current.state.as_of,
                    added_observations=tuple(
                        item
                        for item in current.state.observation_ids
                        if item not in set(previous.state.observation_ids)
                    ),
                    changed_variables=tuple(
                        sorted(
                            name
                            for name in {
                                item.variable
                                for domain in previous.state.domains
                                for item in domain.variables
                            }
                            | {
                                item.variable
                                for domain in current.state.domains
                                for item in domain.variables
                            }
                            if next(
                                (
                                    item.value
                                    for domain in previous.state.domains
                                    for item in domain.variables
                                    if item.variable == name
                                ),
                                None,
                            )
                            != next(
                                (
                                    item.value
                                    for domain in current.state.domains
                                    for item in domain.variables
                                    if item.variable == name
                                ),
                                None,
                            )
                        )
                    ),
                )
            )
        return tuple(result)
