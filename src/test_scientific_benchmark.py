from datetime import UTC, datetime, timedelta

import pytest

from .scientific_execution import mean_absolute_calibration_error, reliability_curve, sharpness
from .scientific_capability import brier_score, calibration_in_the_large, log_score, rolling_origin_persistence


def test_synthetic_probability_benchmark_is_reproducible() -> None:
    probabilities = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
    outcomes = [0, 0, 0, 1, 1, 1]
    metrics = (
        brier_score(probabilities, outcomes),
        log_score(probabilities, outcomes),
        calibration_in_the_large(probabilities, outcomes),
        mean_absolute_calibration_error(probabilities, outcomes, bins=6),
        sharpness(probabilities),
    )
    assert metrics[0] == pytest.approx(0.0633333333)
    assert metrics[1] < 0
    assert metrics[2] == pytest.approx(0.0)
    assert metrics[3] < 0.2
    assert metrics[4] > 0
    assert reliability_curve(probabilities, outcomes, bins=6) == reliability_curve(probabilities, outcomes, bins=6)


def test_rolling_origin_baseline_has_no_future_information() -> None:
    series = [1.0, 2.0, 4.0, 8.0, 16.0]
    forecasts, outcomes = rolling_origin_persistence(series, min_history=2)
    assert forecasts == [2.0, 4.0, 8.0]
    assert outcomes == [4.0, 8.0, 16.0]


def test_temporal_benchmark_rejects_future_availability() -> None:
    origin = datetime(2026, 9, 16, 12, tzinfo=UTC)
    future = origin + timedelta(minutes=1)
    with pytest.raises(ValueError, match="future information"):
        from .scientific_execution import require_point_in_time
        require_point_in_time([future], origin)
