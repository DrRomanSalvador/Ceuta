from datetime import datetime, timezone

import pytest

from app.core.errors import ContractViolation, TemporalViolation
from app.core.pipeline.contracts import ObservationRecord
from app.core.state.estimation import ScalarKalmanFilter


def observation(observation_id: str, value: float, second: int) -> ObservationRecord:
    timestamp = datetime(2026, 1, 1, 0, 0, second, tzinfo=timezone.utc)
    return ObservationRecord(
        observation_id=observation_id,
        variable="signal",
        value=value,
        unit="u",
        event_time=timestamp,
        available_at=timestamp,
        source_ids=("source",),
        evidence_ids=(observation_id,),
        domain="synthetic",
        quality=1.0,
        provenance_hash=f"hash-{observation_id}",
    )


def test_filter_updates_latent_state_and_increases_process_uncertainty_over_time() -> None:
    first = observation("o1", 10.0, 0)
    second = observation("o2", 14.0, 10)
    estimator = ScalarKalmanFilter(
        variable="signal",
        initial_mean=0.0,
        initial_variance=4.0,
        process_variance_per_second=0.1,
    )

    first_estimate = estimator.update(first, observation_variance=1.0)
    second_estimate = estimator.update(second, observation_variance=1.0)

    assert first_estimate.mean == pytest.approx(8.0)
    assert first_estimate.variance == pytest.approx(0.8)
    assert second_estimate.prior_variance == pytest.approx(1.8)
    assert second_estimate.mean > first_estimate.mean
    assert second_estimate.variance < second_estimate.prior_variance


def test_prediction_explicitly_represents_missing_observation() -> None:
    estimator = ScalarKalmanFilter("signal", 0.0, 1.0, 0.1)
    estimator.update(observation("o1", 5.0, 0), 1.0)

    predicted = estimator.predict_to(datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc))

    assert predicted.observation_id is None
    assert predicted.innovation is None
    assert predicted.mean == pytest.approx(2.5)
    assert predicted.variance == pytest.approx(1.0)
    assert predicted.prior_variance == pytest.approx(2.0)


def test_filter_rejects_time_reversal_and_wrong_variable() -> None:
    estimator = ScalarKalmanFilter("signal", 0.0, 1.0, 0.0)
    estimator.update(observation("o1", 1.0, 10), 1.0)

    with pytest.raises(TemporalViolation):
        estimator.update(observation("o0", 0.0, 9), 1.0)

    wrong = observation("o2", 2.0, 11)
    wrong = ObservationRecord(
        observation_id=wrong.observation_id,
        variable="other",
        value=wrong.value,
        unit=wrong.unit,
        event_time=wrong.event_time,
        available_at=wrong.available_at,
        source_ids=wrong.source_ids,
        evidence_ids=wrong.evidence_ids,
        domain=wrong.domain,
        quality=wrong.quality,
        provenance_hash=wrong.provenance_hash,
    )
    with pytest.raises(ContractViolation):
        estimator.update(wrong, 1.0)


def test_filter_rejects_non_positive_observation_variance() -> None:
    estimator = ScalarKalmanFilter("signal", 0.0, 1.0, 0.0)
    with pytest.raises(ContractViolation):
        estimator.update(observation("o1", 1.0, 0), 0.0)
