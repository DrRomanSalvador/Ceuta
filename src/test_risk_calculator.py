import unittest
from datetime import UTC, datetime

from backend.app.core.epistemology_p0.epistemology.states import EpistemicStatus
from backend.app.core.p0_contracts import EvidenceContract, SourceRelation, Uncertainty

from .risk_calculator import RiskCalculator
from .scientific_capability import DynamicDenominator


class RiskCalculatorTests(unittest.TestCase):
    def _evidence(self, status: EpistemicStatus, source: str = "UN") -> EvidenceContract:
        now = datetime.now(UTC)
        return EvidenceContract(
            evidence_id=f"E-{source}-{status.value}",
            claim='{"incidents": 2}',
            source_id=source,
            observed_at=now,
            ingestion_time=now,
            uncertainty=Uncertainty(
                kind="bounded",
                lower=0.0,
                upper=1.0,
                confidence=0.95,
                description="test evidence",
            ),
            epistemic_status=status,
            source_relation=SourceRelation.INDEPENDENT,
            limitations=("test",),
        )

    def test_risk_calculation_accepts_observed_fact(self):
        result = RiskCalculator().calculate_risk([self._evidence(EpistemicStatus.OBSERVED_FACT)])
        self.assertGreaterEqual(result.risk_score, 0.0)
        self.assertLessEqual(result.risk_score, 1.0)
        self.assertEqual(result.data_sources, ["UN"])

    def test_dynamic_denominator_is_required_for_event_rate(self):
        denominator = DynamicDenominator(
            denominator_id="D-CEUTA-2026",
            population_definition="population at risk",
            population_at_risk=1000,
            period_start=datetime(2026, 1, 1, tzinfo=UTC),
            period_end=datetime(2026, 2, 1, tzinfo=UTC),
            geography="CEUTA",
            definition_version="1",
        )
        result = RiskCalculator().calculate_risk(
            [self._evidence(EpistemicStatus.OBSERVED_FACT)],
            event_count=20,
            denominator=denominator,
        )
        self.assertEqual(result.event_rate, 0.02)
        self.assertEqual(result.denominator_id, "D-CEUTA-2026")
        self.assertIsNotNone(result.event_rate_interval)
        self.assertLess(result.event_rate_interval[0], result.event_rate)
        self.assertGreater(result.event_rate_interval[1], result.event_rate)

    def test_event_rate_cannot_be_built_from_numerator_alone(self):
        with self.assertRaises(ValueError):
            RiskCalculator().calculate_risk(
                [self._evidence(EpistemicStatus.OBSERVED_FACT)], event_count=20
            )

    def test_event_rate_cannot_exceed_denominator(self):
        denominator = DynamicDenominator(
            denominator_id="D-1",
            population_definition="population at risk",
            population_at_risk=10,
            period_start=datetime(2026, 1, 1, tzinfo=UTC),
            period_end=datetime(2026, 2, 1, tzinfo=UTC),
            geography="CEUTA",
            definition_version="1",
        )
        with self.assertRaises(ValueError):
            RiskCalculator().calculate_risk(
                [self._evidence(EpistemicStatus.OBSERVED_FACT)],
                event_count=11,
                denominator=denominator,
            )

    def test_unknown_evidence_cannot_be_promoted_into_risk(self):
        with self.assertRaises(ValueError):
            RiskCalculator().calculate_risk([self._evidence(EpistemicStatus.UNKNOWN)])

    def test_empty_evidence_is_rejected(self):
        with self.assertRaises(ValueError):
            RiskCalculator().calculate_risk([])


if __name__ == "__main__":
    unittest.main()
