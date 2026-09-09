from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.core.adversarial_validation import (
    CandidateCapability,
    DataUseMode,
    EvidenceMaturity,
    ExpertDomain,
    FindingCode,
    FindingSeverity,
    PredictivePerformance,
    TargetLevel,
    ValidationDataset,
    ValidationDecision,
    run_adversarial_validation,
    summarize_report,
    validate_invariants,
)


def _dataset(
    *,
    temporal_split: bool = True,
    external_dataset: bool = True,
    prospective_evaluation: bool = True,
    independent_test_set: bool = True,
    missingness_assessed: bool = True,
    subgroup_evaluation: bool = True,
    drift_assessed: bool = True,
) -> ValidationDataset:
    return ValidationDataset(
        dataset_id="validation-test-001",
        sample_size=10_000,
        positive_events=500,
        negative_events=9_500,
        temporal_split=temporal_split,
        external_dataset=external_dataset,
        prospective_evaluation=prospective_evaluation,
        independent_test_set=independent_test_set,
        missingness_assessed=missingness_assessed,
        subgroup_evaluation=subgroup_evaluation,
        drift_assessed=drift_assessed,
    )


def _performance() -> PredictivePerformance:
    return PredictivePerformance(
        roc_auc=0.82,
        pr_auc=0.41,
        brier_score=0.12,
        calibration_in_the_large=0.01,
        calibration_slope=0.96,
        sensitivity=0.78,
        specificity=0.84,
        false_positive_rate=0.16,
        false_negative_rate=0.22,
        decision_curve_net_benefit=0.08,
        lead_time_minutes=120.0,
    )


def _valid_candidate(**overrides: object) -> CandidateCapability:
    values: dict[str, object] = {
        "capability_id": "ceutia-test-capability",
        "name": "System pressure early-warning capability",
        "target_level": TargetLevel.SYSTEM,
        "data_mode": DataUseMode.INTERNAL,
        "evidence_maturity": EvidenceMaturity.PROSPECTIVELY_VALIDATED,
        "scientific_references": (
            "methodological-reference-001",
            "validation-reference-002",
        ),
        "provenance_complete": True,
        "source_independence_assessed": True,
        "corroboration_assessed": True,
        "contradiction_handling": True,
        "temporal_validation": True,
        "spatial_validation": True,
        "uncertainty_quantified": True,
        "epistemic_separation": True,
        "produces_probability": True,
        "calibration_assessed": True,
        "discrimination_assessed": True,
        "false_positive_cost_assessed": True,
        "false_negative_cost_assessed": True,
        "lead_time_assessed": True,
        "operational_utility_assessed": True,
        "missingness_assessed": True,
        "drift_assessed": True,
        "robustness_assessed": True,
        "subgroup_robustness_assessed": True,
        "privacy_reviewed": True,
        "cybersecurity_reviewed": True,
        "human_oversight_required": True,
        "human_oversight_implemented": True,
        "reproducibility_verified": True,
        "uses_identity_attributes": False,
        "predicts_individual_dangerousness": False,
        "predicts_group_dangerousness": False,
        "automated_operational_action": False,
        "event_definition": "Predefined system-level overload event",
        "prediction_horizon_minutes": 120.0,
        "threshold_definition": "Pre-registered operational threshold",
        "validation_dataset": _dataset(),
        "performance": _performance(),
    }

    values.update(overrides)
    return CandidateCapability(**values)  # type: ignore[arg-type]


def test_invariants_are_structurally_valid() -> None:
    assert validate_invariants() == ()


def test_valid_candidate_passes_all_six_expert_gates() -> None:
    candidate = _valid_candidate()

    report = run_adversarial_validation(
        candidate,
        now=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
    )

    assert report.decision is ValidationDecision.PASS
    assert report.passed
    assert not report.blocked
    assert not report.shadow_only

    assert len(report.expert_results) == 6
    assert {
        result.domain for result in report.expert_results
    } == set(ExpertDomain)

    assert report.findings == ()


def test_missing_provenance_prevents_production() -> None:
    candidate = _valid_candidate(provenance_complete=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.MISSING_PROVENANCE in report.unresolved_major_failures


def test_dependent_sources_are_not_treated_as_independent() -> None:
    candidate = _valid_candidate(source_independence_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.DEPENDENT_SOURCES in report.unresolved_major_failures


def test_unresolved_contradictions_are_detected() -> None:
    candidate = _valid_candidate(contradiction_handling=False)

    report = run_adversarial_validation(candidate)

    assert FindingCode.UNRESOLVED_CONTRADICTION in report.unresolved_major_failures


def test_missing_temporal_validation_blocks_operational_maturity() -> None:
    candidate = _valid_candidate(temporal_validation=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.NO_TEMPORAL_VALIDATION in report.unresolved_major_failures


def test_missing_probability_calibration_is_critical() -> None:
    candidate = _valid_candidate(calibration_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.UNCALIbrATED_PROBABILITY in report.mandatory_failures


def test_missing_probability_discrimination_is_major() -> None:
    candidate = _valid_candidate(discrimination_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.DISCRIMINATION_UNASSESSED in report.unresolved_major_failures


def test_probability_without_uncertainty_is_not_production_ready() -> None:
    candidate = _valid_candidate(uncertainty_quantified=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.UNCERTAINTY_MISSING in report.unresolved_major_failures


def test_missing_outcome_definition_is_detected() -> None:
    candidate = _valid_candidate(event_definition=None)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.OUTCOME_UNDEFINED in report.unresolved_major_failures


def test_missing_prediction_horizon_is_detected() -> None:
    candidate = _valid_candidate(prediction_horizon_minutes=None)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.HORIZON_UNDEFINED in report.unresolved_major_failures


def test_negative_prediction_horizon_is_detected() -> None:
    candidate = _valid_candidate(prediction_horizon_minutes=-1.0)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.HORIZON_UNDEFINED in report.unresolved_major_failures


def test_false_positive_cost_must_be_assessed() -> None:
    candidate = _valid_candidate(false_positive_cost_assessed=False)

    report = run_adversarial_validation(candidate)

    assert FindingCode.FALSE_POSITIVE_COST_UNKNOWN in report.unresolved_major_failures


def test_false_negative_cost_must_be_assessed() -> None:
    candidate = _valid_candidate(false_negative_cost_assessed=False)

    report = run_adversarial_validation(candidate)

    assert FindingCode.FALSE_NEGATIVE_COST_UNKNOWN in report.unresolved_major_failures


def test_lead_time_must_be_measured() -> None:
    candidate = _valid_candidate(lead_time_assessed=False)

    report = run_adversarial_validation(candidate)

    assert FindingCode.LEAD_TIME_UNKNOWN in report.unresolved_major_failures


def test_operational_utility_must_be_evaluated() -> None:
    candidate = _valid_candidate(operational_utility_assessed=False)

    report = run_adversarial_validation(candidate)

    assert FindingCode.UTILITY_UNASSESSED in report.unresolved_major_failures


def test_direct_automated_operational_action_is_critical() -> None:
    candidate = _valid_candidate(automated_operational_action=True)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.AUTOMATED_OPERATIONAL_ACTION in report.mandatory_failures


def test_identity_based_prediction_is_critical() -> None:
    candidate = _valid_candidate(uses_identity_attributes=True)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.IDENTITY_BASED_INFERENCE in report.mandatory_failures


def test_individual_dangerousness_prediction_is_critical() -> None:
    candidate = _valid_candidate(
        target_level=TargetLevel.INDIVIDUAL,
        predicts_individual_dangerousness=True,
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.INDIVIDUAL_DANGEROUSNESS in report.mandatory_failures


def test_group_dangerousness_prediction_is_critical() -> None:
    candidate = _valid_candidate(
        target_level=TargetLevel.GROUP,
        predicts_group_dangerousness=True,
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.GROUP_DANGEROUSNESS in report.mandatory_failures


def test_individual_target_is_not_accepted_by_geospatial_gate() -> None:
    candidate = _valid_candidate(target_level=TargetLevel.INDIVIDUAL)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.INVALID_TARGET in report.unresolved_major_failures


def test_group_target_without_dangerousness_prediction_can_be_reviewed() -> None:
    candidate = _valid_candidate(
        target_level=TargetLevel.GROUP,
        predicts_group_dangerousness=False,
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.PASS


def test_missing_privacy_review_prevents_production() -> None:
    candidate = _valid_candidate(privacy_reviewed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.PRIVACY_VIOLATION in report.unresolved_major_failures


def test_missing_cybersecurity_review_prevents_production() -> None:
    candidate = _valid_candidate(cybersecurity_reviewed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.SECURITY_VIOLATION in report.unresolved_major_failures


def test_missing_reproducibility_prevents_production() -> None:
    candidate = _valid_candidate(reproducibility_verified=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.REPRODUCIBILITY_MISSING in report.unresolved_major_failures


def test_no_scientific_references_prevents_production() -> None:
    candidate = _valid_candidate(scientific_references=())

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.INSUFFICIENT_EVIDENCE in report.unresolved_major_failures


def test_prospective_validation_claim_without_prospective_dataset_is_critical() -> None:
    candidate = _valid_candidate(
        validation_dataset=_dataset(prospective_evaluation=False),
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.INSUFFICIENT_EVIDENCE in report.mandatory_failures


def test_external_validation_claim_requires_external_dataset() -> None:
    candidate = _valid_candidate(
        evidence_maturity=EvidenceMaturity.EXTERNALLY_VALIDATED,
        validation_dataset=_dataset(external_dataset=False),
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.INSUFFICIENT_EVIDENCE in report.mandatory_failures


def test_temporal_validation_claim_without_temporal_validation_is_critical() -> None:
    candidate = _valid_candidate(
        evidence_maturity=EvidenceMaturity.TEMPORALLY_VALIDATED,
        temporal_validation=False,
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.NO_TEMPORAL_VALIDATION in report.mandatory_failures


def test_missing_validation_dataset_is_major_not_silent() -> None:
    candidate = _valid_candidate(validation_dataset=None)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.INSUFFICIENT_EVIDENCE in report.unresolved_major_failures


def test_validation_dataset_with_no_positive_events_is_rejected() -> None:
    dataset = ValidationDataset(
        dataset_id="no-events",
        sample_size=1_000,
        positive_events=0,
        negative_events=1_000,
        temporal_split=True,
        external_dataset=True,
        prospective_evaluation=True,
        independent_test_set=True,
        missingness_assessed=True,
        subgroup_evaluation=True,
        drift_assessed=True,
    )

    candidate = _valid_candidate(validation_dataset=dataset)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.INSUFFICIENT_EVIDENCE in report.unresolved_major_failures


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("roc_auc", -0.1),
        ("roc_auc", 1.1),
        ("pr_auc", -0.1),
        ("pr_auc", 1.1),
        ("brier_score", -0.1),
        ("brier_score", 1.1),
        ("sensitivity", -0.1),
        ("sensitivity", 1.1),
        ("specificity", -0.1),
        ("specificity", 1.1),
        ("false_positive_rate", -0.1),
        ("false_positive_rate", 1.1),
        ("false_negative_rate", -0.1),
        ("false_negative_rate", 1.1),
    ],
)
def test_performance_bounds_are_enforced(
    field: str,
    value: float,
) -> None:
    performance = PredictivePerformance(**{field: value})
    candidate = _valid_candidate(performance=performance)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK


def test_negative_lead_time_is_rejected() -> None:
    performance = PredictivePerformance(lead_time_minutes=-10.0)
    candidate = _valid_candidate(performance=performance)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK


def test_nonfinite_performance_is_rejected() -> None:
    performance = PredictivePerformance(roc_auc=float("nan"))
    candidate = _valid_candidate(performance=performance)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK


def test_missingness_assessment_is_required() -> None:
    candidate = _valid_candidate(missingness_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.MISSINGNESS_UNASSESSED in report.unresolved_major_failures


def test_drift_assessment_is_required() -> None:
    candidate = _valid_candidate(drift_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.DRIFT_UNASSESSED in report.unresolved_major_failures


def test_robustness_assessment_is_required() -> None:
    candidate = _valid_candidate(robustness_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.ROBUSTNESS_UNASSESSED in report.unresolved_major_failures


def test_subgroup_robustness_assessment_is_required() -> None:
    candidate = _valid_candidate(subgroup_robustness_assessed=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert (
        FindingCode.SUBGROUP_ROBUSTNESS_UNASSESSED
        in report.unresolved_major_failures
    )


def test_human_oversight_is_required_for_operational_use() -> None:
    candidate = _valid_candidate(human_oversight_implemented=False)

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY
    assert FindingCode.HUMAN_OVERSIGHT_MISSING in report.unresolved_major_failures


def test_multiple_major_failures_are_preserved() -> None:
    candidate = _valid_candidate(
        provenance_complete=False,
        temporal_validation=False,
        uncertainty_quantified=False,
        privacy_reviewed=False,
        cybersecurity_reviewed=False,
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.SHADOW_ONLY

    expected = {
        FindingCode.MISSING_PROVENANCE,
        FindingCode.NO_TEMPORAL_VALIDATION,
        FindingCode.UNCERTAINTY_MISSING,
        FindingCode.PRIVACY_VIOLATION,
        FindingCode.SECURITY_VIOLATION,
    }

    assert expected.issubset(set(report.unresolved_major_failures))


def test_critical_failure_has_priority_over_major_failures() -> None:
    candidate = _valid_candidate(
        privacy_reviewed=False,
        calibration_assessed=False,
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.BLOCK
    assert FindingCode.UNCALIbrATED_PROBABILITY in report.mandatory_failures
    assert FindingCode.PRIVACY_VIOLATION in report.unresolved_major_failures


def test_assert_operationally_eligible_rejects_shadow_only() -> None:
    from app.core.adversarial_validation import assert_operationally_eligible

    report = run_adversarial_validation(
        _valid_candidate(temporal_validation=False)
    )

    with pytest.raises(RuntimeError, match="SHADOW_ONLY"):
        assert_operationally_eligible(report)


def test_assert_operationally_eligible_rejects_blocked() -> None:
    from app.core.adversarial_validation import assert_operationally_eligible

    report = run_adversarial_validation(
        _valid_candidate(uses_identity_attributes=True)
    )

    with pytest.raises(RuntimeError, match="BLOCKED"):
        assert_operationally_eligible(report)


def test_summary_is_serializable_and_does_not_expose_private_content() -> None:
    report = run_adversarial_validation(
        _valid_candidate(
            provenance_complete=False,
            privacy_reviewed=False,
        )
    )

    summary = summarize_report(report)

    assert summary["capability_id"] == "ceutia-test-capability"
    assert summary["decision"] == ValidationDecision.SHADOW_ONLY.value

    assert "scientific_references" not in summary
    assert "metadata" not in summary
    assert "validation_dataset" not in summary

    domains = summary["domains"]
    assert isinstance(domains, dict)
    assert len(domains) == 6


def test_report_timestamp_is_deterministic_when_supplied() -> None:
    timestamp = datetime(2026, 9, 9, 12, 30, tzinfo=timezone.utc)

    report = run_adversarial_validation(
        _valid_candidate(),
        now=timestamp,
    )

    assert report.generated_at == timestamp


def test_all_six_experts_are_always_executed() -> None:
    candidate = _valid_candidate(
        provenance_complete=False,
        automated_operational_action=True,
        spatial_validation=False,
        privacy_reviewed=False,
        calibration_assessed=False,
    )

    report = run_adversarial_validation(candidate)

    domains = {result.domain for result in report.expert_results}

    assert domains == {
        ExpertDomain.STRATEGIC_INTELLIGENCE,
        ExpertDomain.OPERATIONAL_SECURITY,
        ExpertDomain.EPIDEMIOLOGY_PUBLIC_HEALTH,
        ExpertDomain.GEOSPATIAL_POPULATION,
        ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
        ExpertDomain.STATISTICS_ML,
    }

    assert report.decision is ValidationDecision.BLOCK


def test_a_candidate_cannot_pass_by_hiding_a_critical_problem_in_metadata() -> None:
    candidate = _valid_candidate(
        metadata={
            "identity_risk": "true",
            "dangerousness_model": "enabled",
            "automated_action": "enabled",
        }
    )

    report = run_adversarial_validation(candidate)

    # Metadata cannot override explicit safety controls.
    assert report.decision is ValidationDecision.PASS


def test_system_level_event_prediction_is_allowed_when_all_gates_pass() -> None:
    candidate = _valid_candidate(
        target_level=TargetLevel.EVENT,
        event_definition="Predefined public-order event",
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.PASS


def test_population_level_health_prediction_is_allowed_when_validated() -> None:
    candidate = _valid_candidate(
        target_level=TargetLevel.POPULATION,
        event_definition="Population-level health-system overload event",
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.PASS


def test_information_about_a_group_is_not_equivalent_to_group_dangerousness() -> None:
    candidate = _valid_candidate(
        target_level=TargetLevel.GROUP,
        predicts_group_dangerousness=False,
        event_definition="Aggregate population-flow change",
    )

    report = run_adversarial_validation(candidate)

    assert report.decision is ValidationDecision.PASS
    assert FindingCode.GROUP_DANGEROUSNESS not in report.mandatory_failures


def test_no_expert_domain_can_be_removed_from_the_gate_registry() -> None:
    from app.core.adversarial_validation import EXPERT_GATES

    assert len(EXPERT_GATES) == 6
    assert set(EXPERT_GATES) == set(ExpertDomain)


def test_finding_severities_are_preserved() -> None:
    candidate = _valid_candidate(
        uses_identity_attributes=True,
        temporal_validation=False,
    )

    report = run_adversarial_validation(candidate)

    critical_findings = [
        finding
        for finding in report.findings
        if finding.severity is FindingSeverity.CRITICAL
    ]

    major_findings = [
        finding
        for finding in report.findings
        if finding.severity is FindingSeverity.MAJOR
    ]

    assert critical_findings
    assert major_findings