from dataclasses import replace

import pytest

from app.core.evidence.longitudinal_validation import LongitudinalRecord, point_in_time_snapshot


def _record(**kwargs):
    return LongitudinalRecord(
        entity_id="ceuta",
        time=10.0,
        outcome=0,
        prediction=0.2,
        **kwargs,
    )


def test_point_in_time_snapshot_selects_latest_revision_available_at_cutoff():
    original = _record(observation_id="obs-1", available_at=12.0, revision=1)
    revised = replace(original, prediction=0.8, available_at=18.0, revision=2)

    assert point_in_time_snapshot([original, revised], as_of=15.0) == (original,)
    assert point_in_time_snapshot([original, revised], as_of=20.0) == (revised,)


def test_point_in_time_snapshot_requires_availability_metadata():
    with pytest.raises(ValueError, match="availability|available_at"):
        point_in_time_snapshot([_record(observation_id="obs-1")], as_of=20.0)


def test_point_in_time_snapshot_rejects_future_observation_revision_as_of_cutoff():
    future = _record(observation_id="obs-1", available_at=30.0, revision=1)
    assert point_in_time_snapshot([future], as_of=20.0) == ()
