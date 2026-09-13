from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class WeakSignal:
    signal_id: str
    variable: str
    strength: float
    persistence: float
    novelty: float
    evidence_ids: tuple[str, ...]

    @property
    def score(self) -> float:
        return self.strength * self.persistence * self.novelty

    def __post_init__(self) -> None:
        if not self.signal_id or not self.variable or not self.evidence_ids:
            raise ValueError("weak signal identity and evidence are required")
        for value in (self.strength, self.persistence, self.novelty):
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError("weak signal components must be in [0,1]")


class WeakSignalDetector:
    def detect(self, *, baseline: float, current: float, persistence: float, novelty: float, variable: str, evidence_ids: tuple[str, ...]) -> WeakSignal | None:
        delta = abs(current - baseline)
        strength = min(1.0, delta / max(abs(baseline), 1.0))
        if strength == 0.0:
            return None
        return WeakSignal(f"weak:{variable}:{hash((current, baseline)) & 0xfffffff}", variable, strength, persistence, novelty, evidence_ids)
