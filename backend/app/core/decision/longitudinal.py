"""Longitudinal evaluation contracts for repeated decision outcomes."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LongitudinalObservation:
    entity_id: str
    decision_id: str
    observed_at: str
    value: float

    def __post_init__(self) -> None:
        if not self.entity_id.strip() or not self.decision_id.strip():
            raise ValueError("longitudinal observation requires entity and decision identity")
        self.timestamp()

    def timestamp(self) -> datetime:
        try:
            timestamp = datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("observed_at must use ISO-8601") from exc
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return timestamp


@dataclass(frozen=True, slots=True)
class LongitudinalEvaluation:
    observations: tuple[LongitudinalObservation, ...]
    training_cutoff: str
    evaluation_start: str

    def __post_init__(self) -> None:
        if not self.observations:
            raise ValueError("longitudinal evaluation requires observations")
        cutoff = self._parse(self.training_cutoff)
        start = self._parse(self.evaluation_start)
        if start <= cutoff:
            raise ValueError("evaluation must start after training cutoff")
        timestamps = [item.timestamp() for item in self.observations]
        if any(cutoff < timestamp < start for timestamp in timestamps):
            raise ValueError("observation falls inside the excluded temporal gap")

    @staticmethod
    def _parse(value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("evaluation timestamps must use ISO-8601") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("evaluation timestamps must be timezone-aware")
        return parsed

    def training_observations(self) -> tuple[LongitudinalObservation, ...]:
        cutoff = self._parse(self.training_cutoff)
        return tuple(item for item in self.observations if item.timestamp() <= cutoff)

    def evaluation_observations(self) -> tuple[LongitudinalObservation, ...]:
        start = self._parse(self.evaluation_start)
        return tuple(item for item in self.observations if item.timestamp() >= start)


__all__ = ["LongitudinalEvaluation", "LongitudinalObservation"]
