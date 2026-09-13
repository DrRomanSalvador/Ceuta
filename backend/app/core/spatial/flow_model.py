from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Flow:
    origin: str
    destination: str
    volume: float


class FlowMobilityModel:
    def normalize(self, flows: tuple[Flow, ...]) -> tuple[Flow, ...]:
        total = sum(max(0.0, f.volume) for f in flows)
        if total <= 0.0:
            return ()
        return tuple(Flow(f.origin, f.destination, max(0.0, f.volume) / total) for f in flows)
