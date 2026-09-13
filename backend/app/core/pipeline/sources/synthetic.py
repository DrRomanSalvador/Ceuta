"""Deterministic local source adapter for CeutIA Phase 1.

The adapter has no external dependencies and produces canonical observation
records from an explicit clock and deterministic value sequence. It is used to
validate pipeline mechanics before real source adapters are introduced.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
import math
from uuid import uuid5, NAMESPACE_URL

from ..contracts import ObservationRecord


@dataclass(frozen=True, slots=True)
class SyntheticSource:
    """Generate reproducible observations from a deterministic specification."""

    source_id: str = "synthetic:phase1"
    variable: str = "synthetic.signal"
    domain: str = "synthetic"
    unit: str = "index"
    start_time: datetime = datetime(2026, 1, 1, tzinfo=__import__("datetime").timezone.utc)
    available_delay: timedelta = timedelta(seconds=5)
    values: tuple[float, ...] = (1.0, 1.25, 1.5, 1.25, 1.75)
    quality: float = 1.0

    def __post_init__(self) -> None:
        if not self.source_id or not self.variable or not self.domain:
            raise ValueError("source_id, variable and domain must not be empty")
        if self.start_time.tzinfo is None or self.start_time.utcoffset() is None:
            raise ValueError("start_time must be timezone-aware")
        if self.available_delay < timedelta(0):
            raise ValueError("available_delay cannot be negative")
        if not self.values:
            raise ValueError("values must not be empty")
        if not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between 0 and 1")
        if any(not math.isfinite(float(value)) for value in self.values):
            raise ValueError("all synthetic values must be finite")

    def records(self) -> Iterator[ObservationRecord]:
        """Yield the complete deterministic observation sequence."""
        for index, value in enumerate(self.values):
            event_time = self.start_time + timedelta(minutes=index)
            available_at = event_time + self.available_delay
            observation_id = str(uuid5(NAMESPACE_URL, f"{self.source_id}:{self.variable}:{index}"))
            provenance_hash = self._provenance_hash(index, event_time, available_at, value)
            yield ObservationRecord(
                observation_id=observation_id,
                variable=self.variable,
                value=float(value),
                unit=self.unit,
                event_time=event_time,
                available_at=available_at,
                source_ids=(self.source_id,),
                evidence_ids=(f"{self.source_id}:evidence:{index}",),
                domain=self.domain,
                quality=self.quality,
                provenance_hash=provenance_hash,
            )

    def _provenance_hash(
        self,
        index: int,
        event_time: datetime,
        available_at: datetime,
        value: float,
    ) -> str:
        canonical = "|".join(
            (
                self.source_id,
                self.variable,
                str(index),
                event_time.isoformat(),
                available_at.isoformat(),
                repr(float(value)),
                self.unit,
                self.domain,
            )
        )
        return sha256(canonical.encode("utf-8")).hexdigest()
