"""Validation primitives for predictive reliability and missing-data handling.

Calibration-in-the-large and calibration slope use the standard unpenalized
logistic calibration model. Penalization is deliberately not applied: a ridge
term changes the estimand and can therefore turn a validation statistic into a
model-dependent quantity. Numerical non-identifiability is reported instead
of silently regularized away.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log
from typing import Sequence

from .scientific_evidence import Missingness, ValidationLevel


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    brier_score: float
    calibration_in_the_large: float
    calibration_slope: float | None
    observed_expected_ratio: float | None
    bin_errors: tuple[float, ...]
    n: int
    method: str = "binary_outcome_logistic_calibration"

    @property
    def mean_absolute_bin_error(self) -> float:
        return sum(abs(x) for x in self.bin_errors) / len(self.bin_errors) if self.bin_errors else 0.0


def _logit(probability: float) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("calibration intercept/slope require predictions strictly between 0 and 1")
    return log(probability / (1.0 - probability))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def _fit_logistic_calibration(logits: Sequence[float], outcomes: Sequence[int]) -> tuple[float, float]:
    """Fit the unpenalized logistic calibration model by damped Newton steps.

    The calibration intercept is the maximum-likelihood intercept conditional
    on the fitted slope; no regularization is introduced because doing so
    changes the scientific estimand. Convergence is based on the score vector,
    not an arbitrary parameter-step tolerance. Near-singular information is
    treated as non-identifiability rather than hidden by a ridge penalty.
    """
    intercept = 0.0
    slope = 1.0
    tolerance = 1e-13
    for _ in range(100):
        g0 = 0.0
        g1 = 0.0
        h00 = 0.0
        h01 = 0.0
        h11 = 0.0
        log_likelihood = 0.0
        for x, y in zip(logits, outcomes):
            eta = intercept + slope * x
            p = _sigmoid(eta)
            residual = y - p
            weight = p * (1.0 - p)
            g0 += residual
            g1 += residual * x
            h00 -= weight
            h01 -= weight * x
            h11 -= weight * x * x
            log_likelihood += y * log(p) + (1 - y) * log(1.0 - p)

        if max(abs(g0), abs(g1)) <= tolerance:
            return intercept, slope

        determinant = h00 * h11 - h01 * h01
        information_scale = max(abs(h00 * h11), abs(h01 * h01), 1.0)
        if abs(determinant) <= 1e-14 * information_scale:
            raise ValueError("calibration model is not identifiable from the supplied predictions/outcomes")

        # Newton direction for maximizing the concave log-likelihood.
        step0 = (g0 * h11 - g1 * h01) / determinant
        step1 = (h00 * g1 - h01 * g0) / determinant
        if not all(isfinite(value) for value in (step0, step1)):
            raise ValueError("calibration model is numerically unstable")

        # Backtracking keeps the Newton iteration inside a numerically valid
        # likelihood region without altering the unpenalized objective.
        accepted = False
        scale = 1.0
        for _ in range(60):
            candidate_intercept = intercept - scale * step0
            candidate_slope = slope - scale * step1
            candidate_ll = 0.0
            valid = True
            for x, y in zip(logits, outcomes):
                p = _sigmoid(candidate_intercept + candidate_slope * x)
                if not (0.0 < p < 1.0):
                    valid = False
                    break
                candidate_ll += y * log(p) + (1 - y) * log(1.0 - p)
            if valid and candidate_ll >= log_likelihood:
                intercept = candidate_intercept
                slope = candidate_slope
                accepted = True
                break
            scale *= 0.5
        if not accepted:
            raise ValueError("calibration model failed to make a numerically stable likelihood step")

    raise ValueError("calibration model did not converge")


class PredictiveValidation:
    """Computes calibration summaries without declaring arbitrary pass/fail thresholds."""

    @staticmethod
    def calibration_report(predictions: Sequence[float], outcomes: Sequence[int], *, bins: int = 10) -> CalibrationReport:
        if len(predictions) != len(outcomes) or not predictions:
            raise ValueError("predictions and outcomes must be non-empty and have equal length")
        if bins < 2:
            raise ValueError("bins must be at least 2")
        if any(not isfinite(float(p)) or not 0.0 <= float(p) <= 1.0 for p in predictions):
            raise ValueError("predictions must be finite probabilities in [0,1]")
        if any(o not in (0, 1) for o in outcomes):
            raise ValueError("binary outcomes must be 0 or 1")

        n = len(predictions)
        brier = sum((float(p) - o) ** 2 for p, o in zip(predictions, outcomes)) / n
        logits = tuple(_logit(float(p)) for p in predictions)
        calibration_in_large, calibration_slope = _fit_logistic_calibration(logits, outcomes)
        expected = sum(predictions)
        observed_expected = None if expected == 0.0 else sum(outcomes) / expected

        errors: list[float] = []
        for index in range(bins):
            lower = index / bins
            upper = (index + 1) / bins
            members = [i for i, p in enumerate(predictions) if lower <= p < upper or (index == bins - 1 and p == 1.0)]
            if members:
                predicted = sum(predictions[i] for i in members) / len(members)
                observed = sum(outcomes[i] for i in members) / len(members)
                errors.append(observed - predicted)
        return CalibrationReport(brier, calibration_in_large, calibration_slope, observed_expected, tuple(errors), n)


@dataclass(frozen=True, slots=True)
class MissingDataAssessment:
    mechanism: Missingness
    complete_case_only: bool
    sensitivity_analysis_performed: bool
    imputation_method: str | None = None
    assumptions: tuple[str, ...] = ()

    @property
    def decision_ready(self) -> bool:
        if self.mechanism is Missingness.UNKNOWN:
            return False
        if self.mechanism is Missingness.MNAR and not self.sensitivity_analysis_performed:
            return False
        return not self.complete_case_only or self.imputation_method is not None


@dataclass(frozen=True, slots=True)
class ValidationAssessment:
    validation_level: ValidationLevel
    calibration: CalibrationReport | None
    external_population: str | None = None
    temporal_holdout: bool = False
    geographic_holdout: bool = False
    prospective: bool = False

    @property
    def externally_validated(self) -> bool:
        return self.validation_level in {ValidationLevel.EXTERNAL, ValidationLevel.PROSPECTIVE}


__all__ = ["CalibrationReport", "MissingDataAssessment", "PredictiveValidation", "ValidationAssessment"]
