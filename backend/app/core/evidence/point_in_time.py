"""Point-in-time evidence contracts for revision-aware temporal evaluation.

A longitudinal observation time is not the same thing as the time at which a
specific revision became available to the evaluator. This module keeps those
clocks explicit and provides a fail-closed snapshot operation for retrospective
replay.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Sequence


@dataclass(frozen=True, slots=True)
class TemporalEvidenceRecord:
    """One revision of an observation with explicit availability metadata."""

    observation_id: Hashable
    entity_id: Hashable
    observed_at: float
    available_at: float
    value: float
    revision: int = 0
    valid_from: float | None = None
    valid_to: float | None = None

    def __post_init__(self) -> None:
        for name, value in (("observed_at", self.observed_at), ("available_at", self.available_at), ("value", self.value)):
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.revision < 0:
            raise ValueError("revision must be non-negative")
        if self.valid_from is not None and not isfinite(self.valid_from):
            raise ValueError("valid_from must be finite when provided")
        if self.valid_to is not None and not isfinite(self.valid_to):
            raise ValueError("valid_to must be finite when provided")
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
