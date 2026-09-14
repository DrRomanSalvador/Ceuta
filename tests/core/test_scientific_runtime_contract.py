from app.core.scientific.scientific_runtime_contract import (
    CausalIdentificationStatus,
    CausalRuntimeContract,
    FeatureSupport,
    NoveltyAssessment,
    ReferenceClassAssessment,
    RobustnessGate,
    RuntimeState,
    ScientificRuntimeAssessment,
    ScientificRuntimeLedger,
)


def _assessment(tmp_path, **kwargs):
    return ScientificRuntimeAssessment(
        assessment_id=kwargs.get("assessment_id", "a1"),
        decision_id=kwargs.get("decision_id", "d1"),
        evidence_ids=("e1",),
        provenance_refs=("citation:e1",),
        reference_class=kwargs.get("reference_class", ReferenceClassAssessment("rc1", 100, 10, 1.0, 1.0)),
        novelty=kwargs.get("novelty", NoveltyAssessment((FeatureSupport("x", 0.0, 10.0, 5.0),))),
        causal=kwargs.get("causal"),
        robustness=kwargs.get("robustness"),
        uncertainty=0.1,
        code_revision="test-revision",
        configuration_hash="test-config-hash",
    )


def test_unique_unsupported_reference_class_abstains():
    assessment = _assessment(
        None,
        reference_class=ReferenceClassAssessment("unique-crisis", 2, 10, 1.0, 1.0, unique_event=True),
    )
    assert assessment.state is RuntimeState.ABSTAIN
    assert "reference_class_unsupported" in assessment.findings
    assert assessment.effective_uncertainty >= 0.9


def test_deployment_outside_observed_support_abstains():
    assessment = _assessment(
        None,
        novelty=NoveltyAssessment((FeatureSupport("x", 0.0, 10.0, 15.0),)),
    )
    assert assessment.novelty.extrapolation
    assert assessment.state is RuntimeState.ABSTAIN
    assert "deployment_outside_observed_support" in assessment.findings


def test_causal_claim_requires_identification_contract():
    contract = CausalRuntimeContract(
        "ATE", "intervention", "outcome", ("consistency", "positivity"), True,
    )
    assert contract.status is CausalIdentificationStatus.ABSTAIN
    assessment = _assessment(None, causal=contract)
    assert assessment.state is RuntimeState.ABSTAIN
    assert "causal_identification_unsatisfied" in assessment.findings


def test_robustness_gate_changes_runtime_state():
    gate = RobustnessGate(0.4, -2.0, 3.0, 0.7, -5.0, 5.0)
    assessment = _assessment(None, robustness=gate)
    assert gate.state is RuntimeState.ABSTAIN
    assert assessment.state is RuntimeState.ABSTAIN


def test_runtime_ledger_is_append_only_and_hash_chained(tmp_path):
    ledger = ScientificRuntimeLedger(str(tmp_path / "runtime.sqlite"))
    ledger.append(_assessment(tmp_path, assessment_id="a1"))
    ledger.append(_assessment(tmp_path, assessment_id="a2"))
    assert ledger.verify_integrity()
