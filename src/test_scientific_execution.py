from datetime import UTC, datetime, timedelta

import pytest

from .scientific_execution import (
    ScientificBoundary,
    ScientificExecutionState,
    OutcomeAvailability,
    build_execution_record,
    calibration_slope,
    canonical_digest,
    mean_absolute_calibration_error,
    reliability_curve,
    require_point_in_time,
    sharpness,
)


def test_execution_record_is_reproducible_and_point_in_time_bound() -> None:
    origin = datetime(2026, 9, 16, 12, tzinfo=UTC)
    record = build_execution_record(
        execution_id="exec-1",
        capability_id="forecast-1",
        epistemic_boundary=ScientificBoundary.PREDICTIVE,
        input_ids=["x1", "x2"],
        source_ids=["source-1"],
        model_version="model-v1",
        data_vintage="2026-09-16T11:00Z",
        configuration={"horizon": 1},
        parameters={"alpha": 0.1},
        code_revision="abc123",
        environment="python-3.12",
        executed_at=origin + timedelta(minutes=1),
        output={"p": 0.4},
        prediction_origin=origin,
    )
    assert record.execution_state == ScientificExecutionState.EXECUTED
    assert record.output_digest == canonical_digest({"p": 0.4})
    require_point_in_time([origin - timedelta(seconds=1)], origin)


def test_future_information_is_rejected() -> None:
    origin = datetime(2026, 9, 16, 12, tzinfo=UTC)
    with pytest.raises(ValueError, match="future information"):
        require_point_in_time([origin + timedelta(seconds=1)], origin)


def test_outcome_availability_is_explicit_and_point_in_time() -> None:
    outcome_time = datetime(2026, 9, 16, 13, tzinfo=UTC)
    available_at = outcome_time + timedelta(hours=2)
    outcome = OutcomeAvailability(
        outcome_id="outcome-1",
        outcome_time=outcome_time,
        available_at=available_at,
        observed=True,
        vintage_id="v1",
        definition_version="d1",
    )
    assert not outcome.eligible_at(outcome_time + timedelta(minutes=30))
    assert outcome.eligible_at(available_at)


def test_observed_outcome_without_availability_is_rejected() -> None:
    with pytest.raises(ValueError, match="available_at"):
        OutcomeAvailability(
            outcome_id="outcome-1",
            outcome_time=datetime(2026, 9, 16, 13, tzinfo=UTC),
            observed=True,
            vintage_id="v1",
            definition_version="d1",
        )


def test_reliability_curve_and_calibration_error_are_deterministic() -> None:
    curve = reliability_curve([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], bins=2)
    assert curve[0].count == 2
    assert curve[1].count == 2
    assert curve[0].observed_frequency == 0.0
    assert curve[1].observed_frequency == 1.0
    assert mean_absolute_calibration_error([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], bins=2) == pytest.approx(0.15)


def test_calibration_slope_is_neutral_for_matching_logit_scale() -> None:
    probabilities = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
    outcomes = [0, 0, 0, 1, 1, 1]
    slope = calibration_slope(probabilities, outcomes)
    assert slope > 0


def test_calibration_slope_rejects_unidentified_case() -> None:
    with pytest.raises(ValueError, match="not identifiable"):
        calibration_slope([0.2, 0.2, 0.2], [0, 1, 0])


def test_sharpness_is_nonnegative_and_bounded() -> None:
    value = sharpness([0.0, 0.5, 1.0])
    assert value == pytest.approx(1 / 6)
    assert 0 <= value <= 0.25
