from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class ForecastDistribution:
    mean: float
    standard_deviation: float
    lower: float
    upper: float


class ForecastDistributionEngine:
    def build(self, samples: tuple[float, ...], *, z: float = 1.96) -> ForecastDistribution:
        if not samples:
            raise ValueError("samples must not be empty")
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / max(1, len(samples) - 1)
        sd = sqrt(variance)
        margin = z * sd / sqrt(len(samples))
        return ForecastDistribution(mean, sd, mean - margin, mean + margin)
