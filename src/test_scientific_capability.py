from __future__ import annotations

import unittest

from .scientific_capability import (
    BaselineDelta,
    DynamicDenominator,
    EpistemicIdentifiability,
    IdentifiabilityAssessment,
    ObservationProcess,
    ObservationRecord,
    ProbabilisticForecast,
    brier_score,
    calibration_in_the_large,
    compare_baselines,
    expected_binary_loss,
    log_score,
    mean_crps,
    normal_crps,
    point_in_time_filter,
    rolling_origin_persistence,
    wilson_interval,
)


class ScientificCapabilityTests(unittest.TestCase):
    def test_probability_metrics(self):
        probabilities = [0.1, 0.8, 0.7, 0.2]
        outcomes = [0, 1, 1, 0]
        self.assertAlmostEqual(brier_score(probabilities, outcomes), 0.045)
        self.assertLess(log_score(probabilities, outcomes), 0)
        self.assertAlmostEqual(calibration_in_the_large(probabilities, outcomes), 0.05)

    def test_normal_crps_is_non_negative(self):
        self.assertGreaterEqual(normal_crps(0.0, 1.0, 0.0), 0.0)
        forecasts = [
            ProbabilisticForecast(mean=0.0, std=1.0, observed=0.0),
            ProbabilisticForecast(mean=1.0, std=2.0, observed=1.5),
        ]
        self.assertGreaterEqual(mean_crps(forecasts), 0.0)

    def test_baseline_comparison_is_directional_not_a_verdict(self):
        result = compare_baselines({"baseline": [0.1, 0.2], "candidate": [0.2, 0.3]}, [0, 1])
        self.assertIsInstance(result, BaselineDelta)

    def test_decision_loss_is_explicit(self):
        self.assertGreaterEqual(expected_binary_loss(0.8, 1, false_positive_cost=2, false_negative_cost=3), 0.0)

    def test_dynamic_denominator(self):
        denominator = DynamicDenominator("D1", 100.0, "population", "2026-09-16", "Ceuta", "v1")
        self.assertAlmostEqual(denominator.rate(10), 0.1)

    def test_wilson_interval_is_bounded(self):
        low, high = wilson_interval(10, 100)
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)

    def test_point_in_time_filter_rejects_future_information(self):
        records = [ObservationRecord("o1", "2026-09-16T12:00:00+00:00", "2026-09-16T13:00:00+00:00", "v1", 1.0)]
        self.assertEqual(point_in_time_filter(records, "2026-09-16T12:30:00+00:00"), [])

    def test_observation_process_forward(self):
        process = ObservationProcess("O1", "Y=g(S,O,D,R,C)+eps", "COUNT", ("coverage",))
        self.assertIsInstance(process, ObservationProcess)

    def test_non_identifiability_is_preserved(self):
        assessment = IdentifiabilityAssessment(
            quantity_id="STATE-1",
            status=EpistemicIdentifiability.PARTIALLY_IDENTIFIED,
            informed_by=("Y-1",),
            observationally_equivalent_alternatives=("A", "B"),
            uncertainty_description="two mechanisms remain observationally equivalent",
            resolving_data=("SOURCE-2",),
        )
        self.assertEqual(assessment.resolving_data, ("SOURCE-2",))

    def test_rolling_origin_persistence(self):
        forecasts, outcomes = rolling_origin_persistence([1.0, 2.0, 4.0, 8.0], min_history=2)
        self.assertEqual(forecasts, [2.0, 4.0])
        self.assertEqual(outcomes, [4.0, 8.0])
