from app.core.final_epistemic_control import (
    ClosedLoopEvaluation,
    CounterfactualStatus,
    EpistemicContract,
    EpistemicIntegrityEngine,
    EpistemicIntegrityStatus,
    EpistemicSelfCritique,
    EpistemicSelfModel,
    EpistemicTransformation,
    FinalEpistemicController,
    FalsifiabilityStatus,
    FalsificationCondition,
    OntologySignal,
    OntologyStatus,
    ProspectiveEvaluationProtocol,
    ProspectiveEvaluationResult,
    RealityAnchorAssessment,
    SystemValidity,
)


def contract(name: str) -> EpistemicContract:
    return EpistemicContract(
        contract_id=name,
        semantic_meaning="rate per population",
        assumptions=("stable definition",),
        provenance_refs=("evidence:1",),
        temporal_reference="2026-01-01T00:00:00Z",
        spatial_reference="ceuta",
        denominator="population",
        population="resident",
        identification_conditions=("defined denominator",),
        causal_interpretation="association",
        evidence_status="observed",
        calibration_conditions=("deployment regime",),
        validity_domain="defined population and period",
        uncertainty_semantics="95% interval",
    )


def anchor() -> RealityAnchorAssessment:
    condition = FalsificationCondition(
        condition_id="f1",
        target_id="state-1",
        expected_observation="stable external indicator",
        falsifying_observation="persistent external contradiction",
        independent_evidence_refs=("external:1",),
    )
    return RealityAnchorAssessment(
        target_id="state-1",
        status=FalsifiabilityStatus.ESTABLISHED,
        conditions=(condition,),
        external_evidence_refs=("external:1",),
        common_mode_dependencies=(),
        divergence_score=0.0,
        global_model_doubt=False,
        reasons=(),
    )


def self_model() -> EpistemicSelfModel:
    return EpistemicSelfModel(
        version="sm-1",
        assumptions=("a1",),
        limitations=("l1",),
        identification_limits=(),
        ontology_status=OntologyStatus.NORMAL,
        ontology_version="ontology-1",
        unexplained_signals=(),
        global_validity=SystemValidity.SUPPORTED,
    )


def prospective_protocol(protocol_id: str = "p1", precommitted: bool = True) -> ProspectiveEvaluationProtocol:
    return ProspectiveEvaluationProtocol(
        protocol_id=protocol_id, target="decision", population="ceuta", context="deployment",
        horizon="12m", decision_rule="precommitted", comparator="baseline",
        outcome="decision_quality", protocol_version="1", system_version="1",
        model_version="1", ontology_version="1", policy_version="1", precommitted=precommitted,
    )


def test_broken_composition_cannot_be_hidden():
    transformation = EpistemicTransformation(
        transformation_id="t1",
        source_contract=contract("in"),
        output_contract=contract("out"),
        preserves=("provenance",),
        breaks=("denominator",),
        justification="aggregation changed denominator semantics",
    )
    assert EpistemicIntegrityEngine.aggregate((transformation,)) is EpistemicIntegrityStatus.BROKEN


def test_intervention_requires_explicit_counterfactual_state():
    outcome = ClosedLoopEvaluation(
        decision_id="d1",
        intervention_id="i1",
        observed_outcome=0.0,
        expected_outcome=1.0,
        counterfactual_status=CounterfactualStatus.UNIDENTIFIABLE,
        policy_induced_change=True,
        observation_process_changed=True,
        target_distribution_changed=True,
        prediction_quality_status="not_interpreted_from_outcome",
        causal_effect_status="unidentified",
        decision_quality_status="unknown",
    )
    assert outcome.counterfactual_status is CounterfactualStatus.UNIDENTIFIABLE


def test_ontology_suspicion_requires_persistence_and_structure():
    signal = OntologySignal("s1", "persistent new structure", 0.9, 0.9, 0.2, 0.8, 0.1, 0.9)
    assert EpistemicSelfCritique.assess((signal,)) is OntologyStatus.ONTOLOGY_REVIEW_REQUIRED
    assert not EpistemicSelfCritique.candidate_revision_allowed(OntologyStatus.ONTOLOGY_REVIEW_REQUIRED, False)
    assert EpistemicSelfCritique.candidate_revision_allowed(OntologyStatus.ONTOLOGY_REVIEW_REQUIRED, True)


def test_controller_does_not_claim_method_effectiveness_without_prospective_evidence():
    protocol = prospective_protocol()
    result = ProspectiveEvaluationResult("p1", None, True, "empirically_unvalidated")
    assessment = FinalEpistemicController().assess(
        reality_anchor=anchor(), transformations=(), self_model=self_model(),
        prospective_protocol=protocol, prospective_result=result,
    )
    assert not assessment.method_effectiveness_established


def test_controller_requires_precommitted_protocol_for_effectiveness():
    protocol = prospective_protocol(precommitted=False)
    result = ProspectiveEvaluationResult("p1", 0.4, True, "prospectively_validated")
    assessment = FinalEpistemicController().assess(
        reality_anchor=anchor(), transformations=(), self_model=self_model(),
        prospective_protocol=protocol, prospective_result=result,
    )
    assert not assessment.method_effectiveness_established


def test_controller_requires_result_to_match_active_protocol():
    protocol = prospective_protocol("p1")
    result = ProspectiveEvaluationResult("different-protocol", 0.4, True, "prospectively_validated")
    assessment = FinalEpistemicController().assess(
        reality_anchor=anchor(), transformations=(), self_model=self_model(),
        prospective_protocol=protocol, prospective_result=result,
    )
    assert not assessment.method_effectiveness_established
    assert "prospective result is not linked to the active protocol" in assessment.reasons


def test_controller_enters_global_doubt():
    doubtful = RealityAnchorAssessment(
        target_id="state-1", status=FalsifiabilityStatus.PARTIAL, conditions=(),
        external_evidence_refs=(), common_mode_dependencies=("same_source",),
        divergence_score=0.9, global_model_doubt=True,
        reasons=("persistent model-world divergence",),
    )
    assessment = FinalEpistemicController().assess(
        reality_anchor=doubtful, transformations=(), self_model=self_model()
    )
    assert assessment.validity is SystemValidity.DOUBT
