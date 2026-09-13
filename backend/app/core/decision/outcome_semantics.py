"""Explicit outcome semantics for closed-loop decision evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OutcomeStatus(StrEnum):
    OBSERVED = "observed"
    REPORTED = "reported"
    ESTIMATED = "estimated"
    UNOBSERVED = "unobserved"


@dataclass(frozen=True, slots=True)
class OutcomeDefinition:
    """Defines what an outcome means before it is compared with a forecast."""

    outcome_id: str
    target: str
    estimand: str
    measurement: str
    unit: str
    direction: str
    time_zero: str
    horizon: str
    observation_window: str

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.outcome_id,
                self.target,
                self.estimand,
                self.measurement,
                self.unit,
                self.direction,
                self.time_zero,
                self.horizon,
                self.observation_window,
            )
        ):
            raise ValueError("outcome definition requires target, estimand, measurement and temporal semantics")
        if self.direction not in {"higher_is_better", "lower_is_better", "bidirectional"}:
            raise ValueError("outcome direction must be explicit")


@dataclass(frozen=True, slots=True)
class OutcomeObservation:
    """Observed or otherwise qualified outcome value; status cannot be inferred from presence alone."""

    outcome_id: str
    value: float | None
    status: OutcomeStatus
    observed_at: str
    source_refs: tuple[str, ...] = ()
    observation_window: str = ""

    def __post_init__(self) -> None:
        if not self.outcome_id.strip() or not self.observed_at.strip():
            raise ValueError("outcome observation requires identity and observation time")
        if self.status is OutcomeStatus.OBSERVED and self.value is None:
            raise ValueError("observed outcome requires a value")
        if self.status in {OutcomeStatus.OBSERVED, OutcomeStatus.REPORTED, OutcomeStatus.ESTIMATED} and not self.source_refs:
            raise ValueError("qualified outcome requires source references")


@dataclass(frozen=True, slots=True)
class OutcomeSemantics:
    definition: OutcomeDefinition
    observation: OutcomeObservation

    def decision_comparable(self) -> bool:
        return (
            self.observation.outcome_id == self.definition.outcome_id
            and self.observation.status is OutcomeStatus.OBSERVED
            and self.observation.value is not None
            and bool(self.observation.observation_window)
            and self.observation.observation_window == self.definition.observation_window
        )


__all__ = ["OutcomeDefinition", "OutcomeObservation", "OutcomeSemantics", "OutcomeStatus"]
