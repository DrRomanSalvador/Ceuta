"""Temporal alignment without silent interpolation or information leakage."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite
from typing import Sequence

from .sensing import RawSignal


@dataclass(frozen=True, slots=True)
class AlignmentWindow:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.start.utcoffset() is None or self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("alignment bounds must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("alignment window must be ordered")


@dataclass(frozen=True, slots=True)
class AlignedValue:
    signal_id: str
    target_time: datetime
    value: float
    source_event_time: datetime
    age_seconds: float
    method: str
    interpolated: bool


class TemporalAligner:
    """Aligns heterogeneous signals using only information available at target time."""

    @staticmethod
    def as_of(signals: Sequence[RawSignal], target: datetime) -> tuple[RawSignal, ...]:
        if target.tzinfo is None or target.utcoffset() is None:
            raise ValueError("target must be timezone-aware")
        return tuple(item for item in signals if item.event_time <= target and item.available_at <= target)

    def latest(self, signals: Sequence[RawSignal], target: datetime, max_age: timedelta | None = None) -> AlignedValue | None:
        eligible = self.as_of(signals, target)
        if not eligible:
            return None
        chosen = max(eligible, key=lambda item: (item.event_time, item.available_at))
        age = (target - chosen.event_time).total_seconds()
        if max_age is not None and age > max_age.total_seconds():
            return None
        return AlignedValue(chosen.signal_id, target, chosen.value, chosen.event_time, age, "last_observation_carried_forward", False)

    def linear_interpolation(self, signals: Sequence[RawSignal], target: datetime, max_gap: timedelta) -> AlignedValue | None:
        if max_gap <= timedelta(0):
            raise ValueError("max_gap must be positive")
        eligible = sorted(self.as_of(signals, target), key=lambda item: item.event_time)
        before = [item for item in eligible if item.event_time <= target]
        after = [item for item in signals if item.event_time >= target and item.available_at <= target]
        if not before or not after:
            return None
        left, right = before[-1], min(after, key=lambda item: item.event_time)
        if left.event_time == right.event_time:
            return AlignedValue(left.signal_id, target, left.value, left.event_time, 0.0, "exact", False)
        gap = right.event_time - left.event_time
        if gap > max_gap or left.signal_id != right.signal_id:
            return None
        alpha = (target - left.event_time).total_seconds() / gap.total_seconds()
        value = left.value + alpha * (right.value - left.value)
        if not isfinite(value):
            return None
        return AlignedValue(left.signal_id, target, value, left.event_time, (target-left.event_time).total_seconds(), "linear_interpolation", True)
