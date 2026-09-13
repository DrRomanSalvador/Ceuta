from app.core.evidence.predictive_validation import PredictiveValidation


def test_calibration_report_exposes_logistic_intercept_and_slope() -> None:
    predictions = (0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9)
    outcomes = (0, 0, 0, 0, 1, 1, 1, 1)
    report = PredictiveValidation.calibration_report(predictions, outcomes)
    assert report.n == len(predictions)
    assert report.calibration_slope is not None
    assert report.calibration_in_the_large == report.calibration_in_the_large
