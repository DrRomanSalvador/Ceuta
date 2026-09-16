from datetime import UTC, datetime, timedelta
import unittest

from .scientific_execution import mean_absolute_calibration_error, reliability_curve, sharpness
from .scientific_capability import brier_score, calibration_in_the_large, log_score, rolling_origin_persistence


class ScientificBenchmarkTests(unittest.TestCase):
    def test_synthetic_probability_benchmark_is_reproducible(self) -> None:
        probabilities = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
        outcomes = [0, 0, 0, 1, 1, 1]
        metrics = (
            brier_score(probabilities, outcomes), log_score(probabilities, outcomes),
            calibration_in_the_large(probabilities, outcomes),
            mean_absolute_calibration_error(probabilities, outcomes, bins=6), sharpness(probabilities),
        )
        self.assertAlmostEqual(metrics[0], 0.0466666667, places=8)
        self.assertLess(metrics[1], 0)
        self.assertAlmostEqual(metrics[2], 0.0)
        self.assertLess(metrics[3], 0.2)
        self.assertGreater(metrics[4], 0)
        self.assertEqual(reliability_curve(probabilities, outcomes, bins=6), reliability_curve(probabilities, outcomes, bins=6))

    def test_rolling_origin_baseline_has_no_future_information(self) -> None:
        forecasts, outcomes = rolling_origin_persistence([1.0, 2.0, 4.0, 8.0, 16.0], min_history=2)
        self.assertEqual(forecasts, [2.0, 4.0, 8.0])
        self.assertEqual(outcomes, [4.0, 8.0, 16.0])

    def test_temporal_benchmark_rejects_future_availability(self) -> None:
        origin = datetime(2026, 9, 16, 12, tzinfo=UTC)
        future = origin + timedelta(minutes=1)
        from .scientific_execution import require_point_in_time
        with self.assertRaisesRegex(ValueError, "future information"):
            require_point_in_time([future], origin)
