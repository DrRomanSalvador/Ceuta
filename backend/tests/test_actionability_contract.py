from datetime import datetime, timezone, timedelta

import pytest

from app.core.actionability import (
    ActionabilityAssessment,
    ActionabilityClient,
    ActionabilityOption,
    ActionabilityStatus,
    ActionabilityTrace,
    ProbabilityStatus,
    validate_actionability_chain,
)


NOW = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)


def assessment(**overrides):
    values = dict(
        assessment_id="a-1",
        client_type=ActionabilityClient.PERSONA,
        subject_or_territory="subject-1",
        problem_definition="defined problem",
        population_scope="target population",
        denominator_id=None,
        evidence_refs=("e-1",),
        evidence_level="EVIDENCE_SUPPORTED",
        applicability_status="SUPPORTED",
        applicability_reasons=("population and context assessed",),
        risk_state="UNCERTAIN",
        risk_probability=None,
        risk_probability_status=ProbabilityStatus.NOT_AVAILABLE,
        risk_uncertainty=0.4,
        consequence="defined consequence",
        exposure="defined exposure",
        time_horizon="7d",
        alternative_explanations=("reporting change",),
        options=(ActionabilityOption("o-1", "observe", "target", "monitor", "detect change"),),
        resource_requirements=(),
        potential_harms=("false reassurance",),
        reversibility="reversible",
        recommended_next_step="monitor",
        decision_authority=None,
        activation_triggers=("threshold",),
        withdrawal_triggers=("expiry",),
        monitoring_indicators=("indicator",),
        outcome_definition=None,
        evaluation_plan=None,
        provenance=("claim:e-1",),
        created_at=NOW,
        information_cutoff=NOW,
        expiry=NOW + timedelta(days=1),
        status=ActionabilityStatus.CONDITIONALLY_ACTIONABLE,
    )
    values.update(overrides)
    return ActionabilityAssessment(**values)


def test_evidence_confidence_cannot_become_probability():
    with pytest.raises(ValueError, match="CALIBRATED"):
        assessment(risk_probability=0.8, risk_probability_status=ProbabilityStatus.UNCALIBRATED)


def test_estado_requires_explicit_denominator():
    with pytest.raises(ValueError, match="denominator_id"):
        assessment(client_type=ActionabilityClient.ESTADO)


def test_intervention_status_requires_evaluable_outcome():
    with pytest.raises(ValueError, match="outcome and evaluation"):
        assessment(status=ActionabilityStatus.INTERVENTION_RELEVANT)


def test_actionability_does_not_create_decision_authority():
    item = assessment()
    assert item.decision_authority is None
    assert item.can_claim_actionability()
    assert not item.requires_human_authority()


def test_actionability_chain_never_infers_missing_stages():
    item = assessment()
    trace = ActionabilityTrace(assessment_id="a-1", intervention_ref="i-1")
    errors = validate_actionability_chain(item, trace)
    assert "intervention cannot be recorded without a decision reference" in errors


def test_outcome_validation_requires_evaluation_trace():
    item = assessment(
        status=ActionabilityStatus.OUTCOME_VALIDATED,
        outcome_definition="defined outcome",
        evaluation_plan="predefined evaluation",
        decision_authority="authorized actor",
    )
    errors = validate_actionability_chain(item, ActionabilityTrace(assessment_id="a-1"))
    assert "OUTCOME_VALIDATED requires an evaluation trace" in errors
