import unittest
from datetime import UTC, datetime, timedelta

from .scientific_capability import (
    BaselineScore,
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
)


class ScientificCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.t0 = datetime(2026, 1, 1, tzinfo=UTC)

    def observation(self, offset_days: int, knowledge_delay: int = 0, vintage: str = "v1"):
        observed = self.t0 + timedelta(days=offset_days)
        knowledge = observed + timedelta(days=knowledge_delay)
        return ObservationRecord(
            observation_id=f"O-{offset_days}-{vintage}",
            phenomenon_id="P-1",
            value=float(offset_days),
            event_time=observed,
            observed_at=observed,
            publication_time=knowledge,
            revision_time=None,
            knowledge_time=knowledge,
            vintage_id=vintage,
            source_id="SOURCE-1",
        )

    def test_point_in_time_filter_blocks_future_information(self):
        origin = self.t0 + timedelta(days=2)
        records = [self.observation(0), self.observation(1, knowledge_delay=2), self.observation(3)]
        eligible = point_in_time_filter(records, origin)
        self.assertEqual([item.observation_id for item in eligible], ["O-0-v1"])

    def test_revision_vintage_remains_explicit(self):
        first = self.observation(1, knowledge_delay=1, vintage="v1")
        revised = self.observation(1, knowledge_delay=5, vintage="v2")
        origin = self.t0 + timedelta(days=3)
        eligible = point_in_time_filter([first, revised], origin)
        self.assertEqual([item.vintage_id for item in eligible], ["v1"])

    def test_dynamic_denominator_requires_population_at_risk(self):
        denominator = DynamicDenominator(
            denominator_id="D-1",
            population_definition="population at risk",
            population_at_risk=1000,
            exposed_population=500,
            observed_population=800,
            period_start=self.t0,
            period_end=self.t0 + timedelta(days=1),
            geography="CEUTA",
            coverage_fraction=0.8,
            definition_version="1",
        )
        self.assertAlmostEqual(denominator.rate(20), 0.02)

    def test_observation_process_is_explicit_and_invertible_only_when_identified(self):
        process = ObservationProcess(
            process_id="OBS-1",
            phenomenon_id="P-1",
            detection_probability=0.5,
            reporting_fraction=0.8,
            coverage_fraction=0.5,
        )
        self.assertAlmostEqual(process.expected_observed_events(100), 20.0)
        self.assertAlmostEqual(process.infer_latent_events(20), 100.0)

        unknown = ObservationProcess(process_id="OBS-2", phenomenon_id="P-1")
        self.assertIsNone(unknown.infer_latent_events(20))
        with self.assertRaises(ValueError):
            unknown.expected_observed_events(20)

    def test_non_identifiable_state_requires_equivalent_alternative(self):
        with self.assertRaises(ValueError):
            IdentifiabilityAssessment(
                quantity_id="STATE-1",
                status=EpistemicIdentifiability.NOT_IDENTIFIABLE,
                uncertainty_description="insufficient observations",
            )

    def test_identifiability_preserves_resolving_data(self):
        assessment = IdentifiabilityAssessment(
            quantity_id="STATE-1",
            status=EpistemicIdentifiability.PARTIALLY_IDENTIFIED,
            informed_by=("Y-1",),
            observationally_equivalent_alternatives=("A", "B"),
            uncertainty_description="two mechanisms remain observationally equivalent",
            resolving_data=("SOURCE-2",),
        )
        self.assertEqual(assessment.resolving_data, ("SOURCE-2",))

    def test_probability_metrics(self):
        probabilities = [0.1, 0.8, 0.7, 0.2]
        outcomes = [0, 1, 1, 0]
        self.assertAlmostEqual(brier_score(probabilities, outcomes), 0.075)
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
        baseline = BaselineScore(name="baseline", brier=0.20, log_score=-0.60, crps=0.40, lead_time=1.0)
        candidate = BaselineScore(name="candidate", brier=0.15, log_score=-0.50, crps=0.30, lead_time=1.5)
        result = compare_baselines(baseline, candidate)
        self.assertLess(result.delta_brier, 0)
        self.assertGreater(result.delta_log_score, 0)
        self.assertLess(result.delta_crps, 0)
        self.assertTrue(result.has_any_improvement)

    def test_expected_utility_is_exposed_as_action_comparison(self):
        no_action, action = expected_binary_loss(
            0.8,
            action_cost=1.0,
            false_positive_cost=2.0,
            false_negative_cost=10.0,
        )
        self.assertEqual(no_action, 8.0)
        self.assertEqual(action, 1.4)
        self.assertLess(action, no_action)


if __name__ == "__main__":
    unittest.main()
