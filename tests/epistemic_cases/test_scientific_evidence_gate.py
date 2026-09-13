from app.core.evidence.scientific_evidence import (
    Certainty,
    EvidenceClass,
    GateDisposition,
    Missingness,
    ScientificEvidence,
    ScientificEvidenceGate,
    ValidationLevel,
)


def test_low_quality_prediction_requires_review() -> None:
    result = ScientificEvidenceGate().evaluate(
        [
            ScientificEvidence(
                evidence_id="model-1",
                evidence_class=EvidenceClass.METHODOLOGICAL,
                peer_reviewed=True,
                doi_verified=True,
                validation_level=ValidationLevel.INTERNAL,
                calibrated=False,
                high_impact=True,
            )
        ]
    )
    assert result.disposition is GateDisposition.HUMAN_REVIEW
    assert result.epistemic_uncertainty >= 0.8
    assert any("external_validation" in item for item in result.required_controls)
    assert any("calibration_assessment" in item for item in result.required_controls)


def test_mnar_without_sensitivity_is_not_decision_ready() -> None:
    result = ScientificEvidenceGate().evaluate(
        [
            ScientificEvidence(
                evidence_id="evidence-1",
                evidence_class=EvidenceClass.EMPIRICAL_VALIDATION,
                peer_reviewed=True,
                doi_verified=True,
                certainty=Certainty.MODERATE,
                validation_level=ValidationLevel.EXTERNAL,
                calibrated=True,
                missingness=Missingness.MNAR,
                missingness_sensitivity=False,
            )
        ]
    )
    assert result.disposition is GateDisposition.HUMAN_REVIEW
    assert "evidence-1:mnar_sensitivity_analysis" in result.required_controls


def test_inadmissible_source_abstains() -> None:
    result = ScientificEvidenceGate().evaluate(
        [
            ScientificEvidence(
                evidence_id="blog-1",
                evidence_class=EvidenceClass.BLOG,
                peer_reviewed=False,
                doi_verified=False,
            )
        ]
    )
    assert result.disposition is GateDisposition.ABSTAIN
    assert result.epistemic_uncertainty == 1.0


def test_external_validated_evidence_can_pass() -> None:
    result = ScientificEvidenceGate().evaluate(
        [
            ScientificEvidence(
                evidence_id="model-validated",
                evidence_class=EvidenceClass.EMPIRICAL_VALIDATION,
                peer_reviewed=True,
                doi_verified=True,
                certainty=Certainty.HIGH,
                risk_of_bias=0.1,
                applicability=0.95,
                validation_level=ValidationLevel.EXTERNAL,
                calibrated=True,
                decision_utility_evaluated=True,
                harms_evaluated=True,
                human_factors_evaluated=True,
                high_impact=True,
            )
        ]
    )
    assert result.disposition is GateDisposition.ALLOW
    assert result.epistemic_uncertainty == 0.0
