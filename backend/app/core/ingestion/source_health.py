from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceHealth:
    source_id: str
    availability: float
    freshness: float
    error_rate: float
    healthy: bool


class SourceHealthMonitor:
    def assess(self, source_id: str, *, availability: float, freshness: float, error_rate: float) -> SourceHealth:
        healthy = availability >= 0.95 and freshness >= 0.8 and error_rate <= 0.05
        return SourceHealth(source_id, availability, freshness, error_rate, healthy)
