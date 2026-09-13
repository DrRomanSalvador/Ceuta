"""Observation-process and data-quality diagnostics for live monitoring."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .sensing import RawSignal, SignalDescriptor


class QualityFlag(str, Enum):
    VALID = "valid"
    RANGE_VIOLATION = "range_violation"
    LOW_QUALITY = "low_quality"
    STALE = "stale"
    DUPLICATE = "duplicate"
    PROCESS_CHANGE = "observation_process_change"


@dataclass(frozen=True, slots=True)
class QualityAssessment:
    signal_id: str
    flags: tuple[QualityFlag, ...]
    score: float
    reason: str

    @property
    def usable(self) -> bool:
        return QualityFlag.VALID in self.flags and not any(flag in self.flags for flag in (QualityFlag.RANGE_VIOLATION, QualityFlag.DUPLICATE))


class ObservationQualityEngine:
    """Separates data validity from epistemic interpretation."""

    def assess(self, signal: RawSignal, descriptor: SignalDescriptor, *, now=None, stale_after_seconds: float | None = None) -> QualityAssessment:
        flags: list[QualityFlag] = []
        score = signal.quality
        reasons: list[str] = []
        if descriptor.expected_range is not None:
            low, high = descriptor.expected_range
            if not low <= signal.value <= high:
                flags.append(QualityFlag.RANGE_VIOLATION)
                reasons.append("declared range violation")
        if signal.quality < 0.5:
            flags.append(QualityFlag.LOW_QUALITY)
            reasons.append("producer quality below 0.5")
        if now is not None and stale_after_seconds is not None:
            age = (now - signal.event_time).total_seconds()
            if age > stale_after_seconds:
                flags.append(QualityFlag.STALE)
                reasons.append("observation exceeds freshness horizon")
        if not flags:
            flags.append(QualityFlag.VALID)
        return QualityAssessment(signal.signal_id, tuple(flags), max(0.0, min(1.0, score)), "; ".join(reasons) or "no quality defect detected")

    @staticmethod
    def duplicate_hashes(signals: Sequence[RawSignal]) -> frozenset[str]:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for item in signals:
            if item.payload_hash in seen:
                duplicates.add(item.payload_hash)
            seen.add(item.payload_hash)
        return frozenset(duplicates)
