import unittest
from datetime import UTC, datetime

from backend.app.core.epistemology_p0.epistemology.states import EpistemicStatus
from backend.app.core.p0_contracts import EvidenceContract, SourceRelation, Uncertainty

from .risk_calculator import RiskCalculator


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

    def test_unknown_evidence_cannot_be_promoted_into_risk(self):
        with self.assertRaises(ValueError):
            RiskCalculator().calculate_risk([self._evidence(EpistemicStatus.UNKNOWN)])

    def test_empty_evidence_is_rejected(self):
        with self.assertRaises(ValueError):
            RiskCalculator().calculate_risk([])


if __name__ == "__main__":
    unittest.main()
