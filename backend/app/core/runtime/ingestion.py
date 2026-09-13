"""Deterministic event-time ingestion for longitudinal monitoring."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from app.core.errors import ContractViolation, TemporalViolation
from .sensing import RawSignal, SensorRegistry


@dataclass(frozen=True, slots=True)
class IngestionDecision:
    accepted: bool
    reason: str
    late: bool = False
    duplicate: bool = False


@dataclass(frozen=True, slots=True)
class IngestionWatermark:
    event_time: datetime
    allowed_lateness: timedelta

    def __post_init__(self) -> None:
        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise TemporalViolation("watermark must be timezone-aware")
        if self.allowed_lateness < timedelta(0):
            raise ContractViolation("allowed lateness cannot be negative")

    @property
    def frontier(self) -> datetime:
        return self.event_time - self.allowed_lateness


class EventTimeIngestor:
    """Validates, deduplicates and orders observations by event time.

    The ingestor never silently rewrites timestamps or drops late data. A late
    event is accepted only when it is inside the configured lateness horizon;
    outside that horizon it is retained as rejected metadata for reconciliation.
    """

    def __init__(self, registry: SensorRegistry, allowed_lateness: timedelta = timedelta(minutes=5)) -> None:
        if allowed_lateness < timedelta(0):
            raise ContractViolation("allowed lateness cannot be negative")
        self.registry = registry
        self.allowed_lateness = allowed_lateness
        self._seen: set[str] = set()
        self._accepted: list[RawSignal] = []
        self._rejected: list[tuple[RawSignal, str]] = []
        self._max_event_time: datetime | None = None

    def ingest(self, signal: RawSignal) -> IngestionDecision:
        self.registry.validate(signal)
        if signal.payload_hash in self._seen:
            return IngestionDecision(False, "duplicate payload", duplicate=True)
        self._seen.add(signal.payload_hash)
        late = self._max_event_time is not None and signal.event_time < self._max_event_time - self.allowed_lateness
        if late:
            self._rejected.append((signal, "outside allowed lateness"))
            return IngestionDecision(False, "outside allowed lateness", late=True)
        self._accepted.append(signal)
        if self._max_event_time is None or signal.event_time > self._max_event_time:
            self._max_event_time = signal.event_time
        return IngestionDecision(True, "accepted", late=signal.event_time < (self._max_event_time or signal.event_time))

    def accepted(self) -> tuple[RawSignal, ...]:
        return tuple(sorted(self._accepted, key=lambda item: (item.event_time, item.available_at, item.payload_hash)))

    def rejected(self) -> tuple[tuple[RawSignal, str], ...]:
        return tuple(self._rejected)

    def watermark(self) -> IngestionWatermark | None:
        if self._max_event_time is None:
            return None
        return IngestionWatermark(self._max_event_time, self.allowed_lateness)

    def replay(self, signals: Iterable[RawSignal]) -> tuple[IngestionDecision, ...]:
        return tuple(self.ingest(signal) for signal in signals)
