"""Decision utility contract distinct from predictive performance metrics."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UtilityDirection(StrEnum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


@dataclass(frozen=True, slots=True)
class UtilityContract:
    utility_id: str
    outcome_id: str
    unit: str
    direction: UtilityDirection
    horizon: str
    stakeholder_scope: str
    harm_definition: str
    constraint_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.utility_id, self.outcome_id, self.unit, self.horizon, self.stakeholder_scope, self.harm_definition)):
            raise ValueError("utility contract is incomplete")

    def accepts_predictive_metric(self, metric_id: str) -> bool:
        """Predictive metrics require an explicit utility mapping; no implicit conversion."""
        return False


__all__ = ["UtilityContract", "UtilityDirection"]
