"""Point-in-time evidence contracts for revision-aware temporal evaluation.

Observation time, source publication time, system acquisition time and effective
validity are distinct clocks. The snapshot contract uses acquisition time as the
information-availability boundary and keeps publication/effective metadata
explicit for provenance and replay.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Sequence


@dataclass(frozen=True, slots=True)
class TemporalEvidenceRecord:
    """One revision of an observation with explicit temporal provenance."""

    observation_id: Hashable
    entity_id: Hashable
    observed_at: float
    available_at: float
    value: float
    revision: int = 0
    published_at: float | None = None
    acquired_at: float | None = None
    valid_from: float | None = None
    valid_to: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("observed_at", self.observed_at),
            ("available_at", self.available_at),
            ("value", self.value),
        ):
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        for name, value in (
            ("published_at", self.published_at),
            ("acquired_at", self.acquired_at),
            ("valid_from", self.valid_from),
            ("valid_to", self.valid_to),
        ):
            if value is not None and not isfinite(value):
                raise ValueError(f"{name} must be finite when provided")
        if self.acquired_at is not None and self.acquired_at > self.available_at:
            raise ValueError("available_at cannot precede acquired_at")
        if self.published_at is not None and self.published_at > self.available_at:
            raise ValueError("available_at cannot precede published_at")
        if self.revision < 0:
            raise ValueError("revision must be non-negative")
        if self.valid_from is not None and self.valid_to is not None and self.valid_from >= self.valid_to:
            raise ValueError("valid_from must be earlier than valid_to")
        if self.valid_from is not None and self.observed_at < self.valid_from:
            raise ValueError("observed_at cannot precede valid_from")
        if self.valid_to is not None and self.observed_at >= self.valid_to:
            raise ValueError("observed_at must precede valid_to")


def point_in_time_snapshot(
    records: Sequence[TemporalEvidenceRecord],
    *,
    as_of: float,
) -> tuple[TemporalEvidenceRecord, ...]:
    """Return the latest revision of each observation known at ``as_of``.

    Records whose availability time is after the cutoff are invisible. Among
    revisions of the same observation, only the highest revision available by
    the cutoff is retained. The function therefore cannot silently use a later
    revision when replaying an earlier information set.
    """
    if not isfinite(as_of):
        raise ValueError("as_of must be finite")
    if any(not isfinite(record.available_at) for record in records):
        raise ValueError("all records require finite available_at metadata")

    eligible = [record for record in records if record.available_at <= as_of]
    selected: dict[Hashable, TemporalEvidenceRecord] = {}
    for record in eligible:
        current = selected.get(record.observation_id)
        if current is None or (record.revision, record.available_at) > (current.revision, current.available_at):
            selected[record.observation_id] = record

    return tuple(
        sorted(selected.values(), key=lambda record: (record.observed_at, str(record.observation_id)))
    )


__all__ = ["TemporalEvidenceRecord", "point_in_time_snapshot"]
