"""Privacy aggregation boundary with explicit non-DP semantics."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class Aggregate:
    count: int
    mean: float


class PrivacyAggregationLayer:
    """Minimum-group aggregation; this class does not implement differential privacy."""

    def aggregate(
        self,
        values: tuple[float, ...],
        *,
        minimum_group_size: int = 10,
    ) -> Aggregate:
        if minimum_group_size <= 0:
            raise ValueError("minimum_group_size must be positive")
        if len(values) < minimum_group_size:
            raise PermissionError("group is below privacy minimum size")
        if not values or any(not math.isfinite(value) for value in values):
            raise ValueError("values must be finite and non-empty")
        return Aggregate(len(values), sum(values) / len(values))
