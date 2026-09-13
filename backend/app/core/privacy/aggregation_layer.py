from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class Aggregate:
    count: int
    mean: float
    noise_scale: float


class PrivacyAggregationLayer:
    def aggregate(self, values: tuple[float, ...], *, epsilon: float, minimum_group_size: int = 10) -> Aggregate:
        if epsilon <= 0.0:
            raise ValueError("epsilon must be positive")
        if len(values) < minimum_group_size:
            raise PermissionError("group is below privacy minimum size")
        mean = sum(values) / len(values)
        return Aggregate(len(values), mean, 1.0 / (epsilon * sqrt(len(values))))
