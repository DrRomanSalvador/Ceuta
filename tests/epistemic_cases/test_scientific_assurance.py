from __future__ import annotations

import pytest

from backend.app.core.evidence.scientific_assurance import (
    AssuranceDisposition,
    CalibrationSlope,
    CausalAssumptions,
    DriftAssessment,
    EarlyWarningMetrics,
    EvidenceDependenceAnalyzer,
    GradeAssessment,
    GradeRating,
    RuntimeSafetyAssessment,
    SourceDependence,
)


def test_grade_certainty_is_conservatively_downgraded() -> None:
    assessment = GradeAssessment(
        initial=GradeRating.HIGH,
        risk_of_bias=GradeRating.HIGH,
        inconsistency=GradeRating.MODERATE,
        indirectness=GradeRating.HIGH,
        imprecision=GradeRating.HIGH,
        publication_bias=GradeRating.HIGH,
    )
    assert assessment.complete
    assert assessment.certainty is GradeRating.MODERATE


def test_common_origin_sources_do_not_count_as_independent() -> None:
    items = (
        SourceDependence("s1", "agency-a", "e1"),
        SourceDependence("s2", "agency-a", "e2"),
        SourceDependence("s3", "independent-b", "e3", 0.8),
    )
    assert EvidenceDependenceAnalyzer.effective_independent_weight(items) == pytest.approx(1.8)
    assert EvidenceDependenceAnalyzer.duplicated_origins(items) == ("agency-a",)


def test_dynamic_policy_requires_causal_assumptions() -> None:
    assert not CausalAssumptions(False, True, True).decision_ready
    assert CausalAssumptions(True, True, True).decision_ready


def test_drift_requires_review_when_calibration_drift_is_unresolved() -> None:
    assert DriftAssessment("baseline", "current", calibration_drift=0.2).requires_model_review
    assert not DriftAssessment("baseline", "current", calibration_drift=0.2, recalibration_performed=True).requires_model_review


def test_early_warning_metrics_reject_invalid_rates() -> None:
    with pytest.raises(ValueError):
        EarlyWarningMetrics(1.1, 0.1, 2.0)


def test_runtime_assurance_abstains_without_independent_monitor() -> None:
    result = RuntimeSafetyAssessment(True, False, True, 0.1, 0.1)
    assert result.disposition is AssuranceDisposition.ABSTAIN


def test_runtime_assurance_requires_review_without_fallback() -> None:
    result = RuntimeSafetyAssessment(True, True, False, 0.1, 0.1)
    assert result.disposition is AssuranceDisposition.HUMAN_REVIEW


def test_calibration_slope_is_estimated_without_arbitrary_thresholds() -> None:
    report = CalibrationSlope.fit((0.2, 0.4, 0.6, 0.8), (0, 0, 1, 1))
    assert report.n == 4
    assert report.slope > 0
