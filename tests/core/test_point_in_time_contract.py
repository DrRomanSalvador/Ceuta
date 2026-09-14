from dataclasses import replace

import pytest

from app.core.evidence.point_in_time import TemporalEvidenceRecord, point_in_time_snapshot


def _record(**kwargs):
    return TemporalEvidenceRecord(
        observation_id="obs-1",
        entity_id="ceuta",
        observed_at=10.0,
        available_at=20.0,
        value=0.2,
        **kwargs,
    )


def test_point_in_time_snapshot_selects_latest_revision_available_at_cutoff():
    original = _record(available_at=12.0, revision=1)
    revised = replace(original, value=0.8, available_at=18.0, revision=2)

    assert point_in_time_snapshot([original, revised], as_of=15.0) == (original,)
    assert point_in_time_snapshot([original, revised], as_of=20.0) == (revised,)


def test_point_in_time_snapshot_requires_explicit_availability_metadata():
    with pytest.raises(TypeError):
        TemporalEvidenceRecord(
            observation_id="obs-1",
            entity_id="ceuta",
            observed_at=10.0,
            value=0.2,
        )


def test_point_in_time_snapshot_excludes_revisions_not_yet_available_at_cutoff():
    future = _record(available_at=30.0, revision=1)
    assert point_in_time_snapshot([future], as_of=20.0) == ()


def test_temporal_evidence_record_rejects_invalid_effective_interval():
    with pytest.raises(ValueError, match="valid_from|valid_to"):
        _record(valid_from=11.0)
    with pytest.raises(ValueError, match="valid_from|valid_to"):
        _record(valid_to=10.0)


def test_temporal_evidence_record_rejects_negative_revision():
    with pytest.raises(ValueError, match="revision"):
        _record(revision=-1)


def test_temporal_evidence_record_keeps_publication_and_acquisition_clocks_distinct():
    record = _record(published_at=12.0, acquired_at=15.0, available_at=15.0)
    assert record.published_at == 12.0
    assert record.acquired_at == 15.0


def test_temporal_evidence_record_rejects_availability_before_source_acquisition():
    with pytest.raises(ValueError, match="available_at|acquired_at"):
        _record(acquired_at=21.0, available_at=20.0)
