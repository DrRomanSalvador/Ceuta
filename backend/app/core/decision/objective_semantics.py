"""Explicit objective semantics and metric interpretation contract."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ObjectiveDirection(StrEnum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


@dataclass(frozen=True, slots=True)
class ObjectiveMetric:
    metric_id: str
    unit: str
    direction: ObjectiveDirection
    horizon: str
    target_definition: str

    def __post_init__(self) -> None:
        if not all((self.metric_id, self.unit, self.horizon, self.target_definition)):
            raise ValueError("objective metric semantics are incomplete")


@dataclass(frozen=True, slots=True)
class DecisionObjective:
    objective_id: str
    metric: ObjectiveMetric
    weight: float
    stakeholder_scope: str

    def __post_init__(self) -> None:
        if not self.objective_id or not self.stakeholder_scope:
            raise ValueError("objective identity and stakeholder scope are required")
        if self.weight < 0:
            raise ValueError("objective weight must be non-negative")


__all__ = ["DecisionObjective", "ObjectiveDirection", "ObjectiveMetric"]
