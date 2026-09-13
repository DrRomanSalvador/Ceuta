from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class CounterfactualResult:
    baseline: float
    intervention: float
    delta: float
    assumptions: tuple[str, ...]


class CounterfactualEngine:
    def evaluate(self, baseline: float, intervention: Callable[[float], float], *, assumptions: tuple[str, ...]) -> CounterfactualResult:
        result = float(intervention(baseline))
        return CounterfactualResult(baseline, result, result - baseline, assumptions)
