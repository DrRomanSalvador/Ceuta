from app.core.final_epistemic_control import (
    EpistemicIntegrityStatus,
    EpistemicSelfModel,
    FalsifiabilityStatus,
    FinalEpistemicAssessment,
    OntologyStatus,
    RealityAnchorAssessment,
    SystemValidity,
)
from app.core.runtime.system_gate import SystemGateDisposition, SystemIntelligenceGate
from app.core.system_intelligence import PredictabilityAssessment, SystemAssessment


def base_system_assessment() -> SystemAssessment:
    return SystemAssessment(
        observable=True,
        identifiable=True,
        predictability=PredictabilityAssessment(True, 0.9, (), False),
        model_disagreement=None,
        missing_data_risk=0.0,
        measurement_process_risk=0.0,
        spatial_dependency=False,
        network_dependency=False,
        regime_changed=False,
        abstain=False,
        reasons=(),
    )


def final_assessment(validity: SystemValidity) -> FinalEpistemicAssessment:
    anchor = RealityAnchorAssessment(
        target_id="x", status=FalsifiabilityStatus.PARTIAL, conditions=(),
        external_evidence_refs=(), common_mode_dependencies=(), divergence_score=0.8,
        global_model_doubt=validity is not SystemValidity.SUPPORTED, reasons=(),
    )
    self_model = EpistemicSelfModel(
        version="1", assumptions=(), limitations=(), identification_limits=(),
        ontology_status=OntologyStatus.ONTOLOGY_REVIEW_REQUIRED if validity is not SystemValidity.SUPPORTED else OntologyStatus.NORMAL,
        ontology_version="1", unexplained_signals=(), global_validity=validity,
    )
    return FinalEpistemicAssessment(
        anchor, EpistemicIntegrityStatus.PRESERVED, None, self_model,
        None, False, validity, ()
    )


def test_final_global_doubt_forces_abstention():
    result = SystemIntelligenceGate().evaluate(base_system_assessment(), final_assessment(SystemValidity.DOUBT))
    assert result.disposition is SystemGateDisposition.ABSTAIN


def test_supported_final_assessment_preserves_normal_gate():
    result = SystemIntelligenceGate().evaluate(base_system_assessment(), final_assessment(SystemValidity.SUPPORTED))
    assert result.disposition is SystemGateDisposition.ALLOW
