from __future__ import annotations

import unittest

from app.core.scientific.epistemic_contracts import (
    ClaimContract,
    DimensionAssessment,
    EvidenceLevel,
    EvidenceAssessment,
    EpistemicState,
    HypothesisContract,
    Identifiability,
    KnowledgeStatus,
    PredictionContract,
    TemporalSemantics,
    claim_strength_is_bounded,
    promotion_allowed,
)


class EpistemicContractTests(unittest.TestCase):
    def test_evidence_is_multidimensional_and_not_scalar(self):
        assessment = EvidenceAssessment(
            certainty=DimensionAssessment(KnowledgeStatus.VALIDATED, 0.9),
            external_validity=DimensionAssessment(KnowledgeStatus.UNKNOWN),
            actionability=DimensionAssessment(KnowledgeStatus.PROVISIONAL, 0.4),
            residual_uncertainty=DimensionAssessment(KnowledgeStatus.ESTIMATED, 0.6),
        )
        self.assertIsNone(assessment.scalar())
        self.assertEqual(assessment.external_validity.status, KnowledgeStatus.UNKNOWN)

    def test_epistemic_promotion_is_adjacent_and_explicit(self):
        self.assertFalse(promotion_allowed(EvidenceLevel.E3_PREDICTIVE_ASSOCIATION, EvidenceLevel.E5_MECHANISM, {"oos": True}))
        self.assertFalse(promotion_allowed(EvidenceLevel.E3_PREDICTIVE_ASSOCIATION, EvidenceLevel.E4_LATENT_STATE, {"oos": False}))
        self.assertTrue(promotion_allowed(EvidenceLevel.E3_PREDICTIVE_ASSOCIATION, EvidenceLevel.E4_LATENT_STATE, {"model": True, "identifiability": True, "uncertainty": True}))

    def test_claim_strength_cannot_exceed_available_evidence(self):
        claim = ClaimContract(
            claim_id="C1", claim_type="predictive", claim_text="x", scope="s", geography="Ceuta",
            population="resident", time_window="2026", source_ids=("S1",), evidence_ids=("E1",),
            model_ids=("M1",), hypothesis_ids=(), alternatives=("H2",), assumptions=("A1",),
            identifiability_status=Identifiability.PARTIALLY_IDENTIFIABLE,
            evidence_level=EvidenceLevel.E3_PREDICTIVE_ASSOCIATION,
            certainty=DimensionAssessment(KnowledgeStatus.PROVISIONAL, 0.7),
            external_validity=DimensionAssessment(KnowledgeStatus.UNKNOWN),
            calibration_status=KnowledgeStatus.PROVISIONAL,
            decision_relevance=KnowledgeStatus.KNOWN,
            actionability=DimensionAssessment(KnowledgeStatus.PROVISIONAL, 0.5),
            failure_modes=("shift",), contradicting_evidence=(), expiry_condition="review", review_date="2026-12-31",
            responsible_mission="CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING",
            epistemic_state=EpistemicState.PREDICTION,
        )
        self.assertTrue(claim_strength_is_bounded(claim, EvidenceLevel.E3_PREDICTIVE_ASSOCIATION))
        self.assertFalse(claim_strength_is_bounded(claim, EvidenceLevel.E2_DESCRIPTIVE_PATTERN))

    def test_prediction_requires_point_in_time_semantics(self):
        prediction = PredictionContract(
            prediction_id="P1", information_cutoff="2026-09-16T10:00:00Z", observation_vintage="2026-09-16",
            feature_availability={"x": "2026-09-16T09:59:00Z"}, forecast_origin="2026-09-16T10:00:00Z",
            forecast_horizon="24h", model_version="m1", target_definition="event", outcome_definition="event",
            point_in_time_fingerprint="pit-1", provenance_ids=("obs-1",),
        )
        self.assertEqual(prediction.model_version, "m1")

    def test_temporal_semantics_do_not_collapse_to_timestamp(self):
        semantics = TemporalSemantics(
            event_time="t1", observation_time="t2", publication_time="t3", ingestion_time="t4",
            revision_time="t5", availability_time="t6", forecast_origin="t7", outcome_time="t8",
        )
        self.assertNotEqual(semantics.event_time, semantics.ingestion_time)

    def test_hypothesis_requires_falsification_and_stopping(self):
        hypothesis = HypothesisContract(
            hypothesis_id="H1", originating_evidence=("E1",), phenomenon="p", mechanism_claim="m",
            alternatives=("H2",), predicted_observations=("o1",), disconfirming_observations=("d1",),
            required_data=("D1",), analysis_plan=("A1",), stopping_rule="stop if no discriminating observation",
            external_validation_plan=("external",), status="NEW",
        )
        self.assertTrue(hypothesis.exploratory)
        self.assertFalse(hypothesis.frozen)


if __name__ == "__main__":
    unittest.main()
