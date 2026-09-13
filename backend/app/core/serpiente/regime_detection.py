from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class Regime:
    regime_id: str
    mean: float
    volatility: float
    observations: int


class RegimeDetector:
    def detect(self, values: tuple[float, ...], *, regime_id: str = "current") -> Regime:
        if not values:
            raise ValueError("values must not be empty")
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return Regime(regime_id, mean, sqrt(variance), len(values))

    @staticmethod
    def changed(previous: Regime, current: Regime, *, mean_threshold: float, volatility_threshold: float) -> bool:
        return abs(current.mean - previous.mean) > mean_threshold or abs(current.volatility - previous.volatility) > volatility_threshold
