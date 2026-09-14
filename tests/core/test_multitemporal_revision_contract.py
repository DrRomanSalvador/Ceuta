from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from app.core.epistemology_p0.temporal.multitemporal import TemporalContext, TemporalFilter


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    version: int
    context: TemporalContext

    @property
    def available_at(self):
        return self.context.available_at

    def is_valid_at(self, simulation_time):
        return self.context.is_valid_at(simulation_time)


BASE = datetime(2026, 1, 1, tzinfo=UTC)


def test_available_at_prioritizes_revision_then_publication_then_ingestion():
    revision_context = TemporalContext(
        publication_time=BASE + timedelta(hours=1),
        ingestion_time=BASE + timedelta(hours=2),
        revision_time=BASE + timedelta(hours=3),
    )
    publication_context = TemporalContext(
        publication_time=BASE + timedelta(hours=1),
        ingestion_time=BASE + timedelta(hours=2),
    )
    ingestion_context = TemporalContext(ingestion_time=BASE + timedelta(hours=2))

    assert revision_context.available_at == BASE + timedelta(hours=3)
    assert publication_context.available_at == BASE + timedelta(hours=1)
    assert ingestion_context.available_at == BASE + timedelta(hours=2)


def test_temporal_context_rejects_invalid_effective_interval():
    with pytest.raises(ValueError, match="valid_from"):
        TemporalContext(valid_from=BASE + timedelta(days=2), valid_to=BASE + timedelta(days=1))


def test_temporal_context_exposes_effective_validity_boundary():
    context = TemporalContext(
        valid_from=BASE + timedelta(hours=1),
        valid_to=BASE + timedelta(hours=3),
    )
    assert context.is_valid_at(BASE + timedelta(hours=1)) is True
    assert context.is_valid_at(BASE + timedelta(hours=2)) is True
    assert context.is_valid_at(BASE + timedelta(hours=3)) is False


def test_snapshot_selects_latest_version_known_at_cutoff():
    first = Evidence("e1", 1, TemporalContext(ingestion_time=BASE + timedelta(hours=1)))
    second = Evidence("e1", 2, TemporalContext(ingestion_time=BASE + timedelta(hours=3)))
    cutoff = BASE + timedelta(hours=2)

    assert TemporalFilter.snapshot_by_available_at([first, second], cutoff) == [first]
    assert TemporalFilter.snapshot_by_available_at([first, second], BASE + timedelta(hours=4)) == [second]


def test_snapshot_excludes_effectively_invalid_evidence_at_cutoff():
    context = TemporalContext(
        ingestion_time=BASE,
        valid_from=BASE + timedelta(hours=2),
        valid_to=BASE + timedelta(hours=4),
    )
    evidence = Evidence("e1", 1, context)
    assert TemporalFilter.snapshot_by_available_at([evidence], BASE + timedelta(hours=1)) == []
    assert TemporalFilter.snapshot_by_available_at([evidence], BASE + timedelta(hours=3)) == [evidence]


def test_snapshot_fails_closed_without_stable_version_identity():
    invalid = Evidence("e1", -1, TemporalContext(ingestion_time=BASE))
    with pytest.raises(ValueError, match="evidence_id|version"):
        TemporalFilter.snapshot_by_available_at([invalid], BASE + timedelta(hours=1))


def test_future_available_evidence_is_excluded_from_snapshot():
    future = Evidence("e1", 1, TemporalContext(ingestion_time=BASE + timedelta(days=1)))
    assert TemporalFilter.snapshot_by_available_at([future], BASE) == []
