from datetime import UTC, datetime, timedelta
import unittest

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


class ScientificExecutionTests(unittest.TestCase):
    def test_execution_record_is_reproducible_and_point_in_time_bound(self) -> None:
        origin = datetime(2026, 9, 16, 12, tzinfo=UTC)
        record = build_execution_record(execution_id="exec-1", capability_id="forecast-1", epistemic_boundary=ScientificBoundary.PREDICTIVE, input_ids=["x1", "x2"], source_ids=["source-1"], model_version="model-v1", data_vintage="2026-09-16T11:00Z", configuration={"horizon": 1}, parameters={"alpha": 0.1}, code_revision="abc123", environment="python-3.12", executed_at=origin + timedelta(minutes=1), output={"p": 0.4}, prediction_origin=origin)
        self.assertEqual(record.execution_state, ScientificExecutionState.EXECUTED)
        self.assertEqual(record.output_digest, canonical_digest({"p": 0.4}))
        require_point_in_time([origin - timedelta(seconds=1)], origin)

    def test_future_information_is_rejected(self) -> None:
        origin = datetime(2026, 9, 16, 12, tzinfo=UTC)
        with self.assertRaisesRegex(ValueError, "future information"):
            require_point_in_time([origin + timedelta(seconds=1)], origin)

    def test_outcome_availability_is_explicit_and_point_in_time(self) -> None:
        outcome_time = datetime(2026, 9, 16, 13, tzinfo=UTC)
        available_at = outcome_time + timedelta(hours=2)
        outcome = OutcomeAvailability(outcome_id="outcome-1", outcome_time=outcome_time, available_at=available_at, observed=True, vintage_id="v1", definition_version="d1")
        self.assertFalse(outcome.eligible_at(outcome_time + timedelta(minutes=30)))
        self.assertTrue(outcome.eligible_at(available_at))

    def test_observed_outcome_without_availability_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "available_at"):
            OutcomeAvailability(outcome_id="outcome-1", outcome_time=datetime(2026, 9, 16, 13, tzinfo=UTC), observed=True, vintage_id="v1", definition_version="d1")

    def test_reliability_curve_and_calibration_error_are_deterministic(self) -> None:
        curve = reliability_curve([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], bins=2)
        self.assertEqual(curve[0].count, 2)
        self.assertEqual(curve[1].count, 2)
        self.assertEqual(curve[0].observed_frequency, 0.0)
        self.assertEqual(curve[1].observed_frequency, 1.0)
        self.assertAlmostEqual(mean_absolute_calibration_error([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], bins=2), 0.15)

    def test_calibration_slope_is_identifiable_and_positive(self) -> None:
        slope = calibration_slope([0.1, 0.2, 0.3, 0.7, 0.8, 0.9], [0, 1, 0, 1, 0, 1])
        self.assertGreater(slope, 0)

    def test_calibration_slope_rejects_unidentified_case(self) -> None:
        with self.assertRaisesRegex(ValueError, "not identifiable"):
            calibration_slope([0.2, 0.2, 0.2], [0, 1, 0])

    def test_sharpness_is_nonnegative_and_bounded(self) -> None:
        value = sharpness([0.0, 0.5, 1.0])
        self.assertAlmostEqual(value, 1 / 6)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 0.25)
