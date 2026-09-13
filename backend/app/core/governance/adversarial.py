from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ManipulationAssessment:
    source_id: str
    indicators: tuple[str, ...]
    risk: float


class AdversarialDetectionEngine:
    def assess(self, source_id: str, *, contradiction_rate: float, coordinated_rate: float, novelty: float) -> ManipulationAssessment:
        for value in (contradiction_rate, coordinated_rate, novelty):
            if not 0.0 <= value <= 1.0:
                raise ValueError("indicators must be in [0,1]")
        risk = min(1.0, 0.4 * contradiction_rate + 0.4 * coordinated_rate + 0.2 * novelty)
        indicators = tuple(name for name, value in (("contradiction", contradiction_rate), ("coordination", coordinated_rate), ("novelty", novelty)) if value >= 0.7)
        return ManipulationAssessment(source_id, indicators, risk)
