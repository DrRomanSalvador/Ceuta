from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

from app.core.epistemology_p0.temporal.multitemporal import TemporalContext, TemporalFilter


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    revision: int
    context: TemporalContext

    @property
    def available_at(self):
        return self.context.available_at


def test_available_at_prioritizes_revision_then_publication_then_ingestion():
    base = datetime(2026, 1, 1)
    revision_context = TemporalContext(
        publication_time=base + timedelta(hours=1),
        ingestion_time=base + timedelta(hours=2),
        revision_time=base + timedelta(hours=3),
    )
    publication_context = TemporalContext(
        publication_time=base + timedelta(hours=1),
        ingestion_time=base + timedelta(hours=2),
    )
    ingestion_context = TemporalContext(ingestion_time=base + timedelta(hours=2))

    assert revision_context.available_at == base + timedelta(hours=3)
    assert publication_context.available_at == base + timedelta(hours=1)
    assert ingestion_context.available_at == base + timedelta(hours=2)


def test_temporal_context_rejects_invalid_effective_interval():
    base = datetime(2026, 1, 1)
    with pytest.raises(ValueError, match="valid_from"):
        TemporalContext(valid_from=base + timedelta(days=2), valid_to=base + timedelta(days=1))


def test_temporal_context_exposes_effective_validity_boundary():
    base = datetime(2026, 1, 1)
    context = TemporalContext(
        valid_from=base + timedelta(hours=1),
        valid_to=base + timedelta(hours=3),
    )
    assert context.is_valid_at(base + timedelta(hours=1)) is True
    assert context.is_valid_at(base + timedelta(hours=2)) is True
    assert context.is_valid_at(base + timedelta(hours=3)) is False


def test_snapshot_selects_latest_revision_known_at_cutoff():
    base = datetime(2026, 1, 1)
    first = Evidence("e1", 1, TemporalContext(ingestion_time=base + timedelta(hours=1)))
    second = Evidence("e1", 2, TemporalContext(ingestion_time=base + timedelta(hours=3)))
    cutoff = base + timedelta(hours=2)

    assert TemporalFilter.snapshot_by_available_at([first, second], cutoff) == [first]
    assert TemporalFilter.snapshot_by_available_at([first, second], base + timedelta(hours=4)) == [second]


def test_snapshot_fails_closed_without_stable_revision_identity():
    base = datetime(2026, 1, 1)
    invalid = Evidence("e1", -1, TemporalContext(ingestion_time=base))
    with pytest.raises(ValueError, match="evidence_id|revision"):
        TemporalFilter.snapshot_by_available_at([invalid], base + timedelta(hours=1))


def test_future_available_evidence_is_excluded_from_snapshot():
    base = datetime(2026, 1, 1)
    future = Evidence("e1", 1, TemporalContext(ingestion_time=base + timedelta(days=1)))
    assert TemporalFilter.snapshot_by_available_at([future], base) == []
