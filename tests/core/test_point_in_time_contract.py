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
