from pytest import approx

from app.core.evidence.predictive_validation import MissingDataAssessment, PredictiveValidation
from app.core.evidence.scientific_evidence import Missingness


def test_calibration_report_keeps_calibration_separate_from_discrimination() -> None:
    report = PredictiveValidation.calibration_report(
        [0.1, 0.2, 0.8, 0.9],
        [0, 0, 1, 1],
        bins=2,
    )
    assert report.n == 4
    assert report.brier_score == approx(0.025)
    assert report.calibration_in_the_large == approx(0.0)
    assert report.observed_expected_ratio == approx(1.0)


def test_mnar_requires_sensitivity_analysis() -> None:
    assessment = MissingDataAssessment(
        mechanism=Missingness.MNAR,
        complete_case_only=False,
        sensitivity_analysis_performed=False,
        imputation_method="multiple_imputation",
    )
    assert not assessment.decision_ready


def test_mcar_with_explicit_handling_can_be_decision_ready() -> None:
    assessment = MissingDataAssessment(
        mechanism=Missingness.MCAR,
        complete_case_only=False,
        sensitivity_analysis_performed=False,
        imputation_method="multiple_imputation",
    )
    assert assessment.decision_ready
