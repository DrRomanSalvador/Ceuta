"""Statistically rigorous predictive validation primitives."""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, sqrt
from statistics import NormalDist
from typing import Sequence

from .scientific_evidence import Missingness, ValidationLevel

_EPS = 1e-15
_Z95 = NormalDist().inv_cdf(0.975)


@dataclass(frozen=True, slots=True)
class Estimate:
    value: float
    standard_error: float | None
    ci_low: float | None
    ci_high: float | None
    estimand: str
    method: str


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    brier_score: float
    log_loss: float
    calibration_in_the_large: float
    calibration_slope: float | None
    calibration_intercept_se: float | None
    calibration_slope_se: float | None
    calibration_intercept_ci: tuple[float, float] | None
    calibration_slope_ci: tuple[float, float] | None
    observed_expected_ratio: float | None
    observed_expected_ratio_ci: tuple[float, float] | None
    brier_skill_score: float | None
    bin_errors: tuple[float, ...]
    n: int
    positive_rate: float
    method: str = "binary_outcome_logistic_calibration"

    @property
    def mean_absolute_bin_error(self) -> float:
        return sum(abs(x) for x in self.bin_errors) / len(self.bin_errors) if self.bin_errors else 0.0


def _logit(p: float) -> float:
    if not 0.0 < p < 1.0:
        raise ValueError("calibration logistic regression requires predictions strictly between 0 and 1")
    return log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    if x >= 0.0:
        z = exp(-x)
        return 1.0 / (1.0 + z)
    z = exp(x)
    return z / (1.0 + z)


def _fit_logistic_calibration(logits: Sequence[float], outcomes: Sequence[int]) -> tuple[float, float, float, float, float]:
    """Fit the standard unpenalized logistic calibration model.

    Model: logit(P(Y=1 | p)) = alpha + beta * logit(p).
    Regularization is deliberately absent because it changes the estimand.
    Separation, singular information and non-convergence are explicit errors.
    The returned covariance matrix is the inverse observed Fisher information.
    """
    if len(logits) != len(outcomes) or len(logits) < 3:
        raise ValueError("at least three paired predictions/outcomes are required")
    if len(set(outcomes)) < 2:
        raise ValueError("calibration is not identifiable with one outcome class")

    alpha, beta = 0.0, 1.0
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = log_likelihood = 0.0
        for x, y in zip(logits, outcomes):
            p = _sigmoid(alpha + beta * x)
            residual = y - p
            weight = p * (1.0 - p)
            g0 += residual
            g1 += residual * x
            h00 -= weight
            h01 -= weight * x
            h11 -= weight * x * x
            log_likelihood += y * log(max(p, _EPS)) + (1 - y) * log(max(1 - p, _EPS))

        determinant = h00 * h11 - h01 * h01
        scale = max(abs(h00 * h11), abs(h01 * h01), 1.0)
        if determinant >= -1e-14 * scale or abs(determinant) <= 1e-14 * scale:
            raise ValueError("calibration information matrix is singular or non-identifiable")
        if max(abs(g0), abs(g1)) <= 1e-12:
            return alpha, beta, h11 / determinant, -h01 / determinant, h00 / determinant

        step_alpha = (g0 * h11 - g1 * h01) / determinant
        step_beta = (h00 * g1 - h01 * g0) / determinant
        accepted = False
        factor = 1.0
        for _ in range(80):
            candidate_alpha = alpha - factor * step_alpha
            candidate_beta = beta - factor * step_beta
            candidate_ll = 0.0
            for x, y in zip(logits, outcomes):
                q = _sigmoid(candidate_alpha + candidate_beta * x)
                candidate_ll += y * log(max(q, _EPS)) + (1 - y) * log(max(1 - q, _EPS))
            if candidate_ll >= log_likelihood:
                alpha, beta = candidate_alpha, candidate_beta
                accepted = True
                break
            factor *= 0.5
        if not accepted:
            raise ValueError("calibration likelihood optimization failed to make an ascent step")

    raise ValueError("calibration model did not converge")


def _wilson_interval(successes: int, n: int) -> tuple[float, float]:
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError("invalid binomial count")
    z = _Z95
    p = successes / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    centre = (p + z2 / (2 * n)) / denominator
    half = z * sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def _auc(predictions: Sequence[float], outcomes: Sequence[int]) -> float | None:
    positives = [float(p) for p, y in zip(predictions, outcomes) if y == 1]
    negatives = [float(p) for p, y in zip(predictions, outcomes) if y == 0]
    if not positives or not negatives:
        return None
    concordant = sum(
        1.0 if positive > negative else 0.5 if positive == negative else 0.0
        for positive in positives for negative in negatives
    )
    return concordant / (len(positives) * len(negatives))


class PredictiveValidation:
    """Compute calibration, discrimination and proper-scoring summaries."""

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
        p = tuple(float(x) for x in predictions)
        y = tuple(int(x) for x in outcomes)
        brier = sum((pi - yi) ** 2 for pi, yi in zip(p, y)) / n
        log_loss = -sum(yi * log(max(pi, _EPS)) + (1 - yi) * log(max(1 - pi, _EPS)) for pi, yi in zip(p, y)) / n
        prevalence = sum(y) / n
        baseline_brier = prevalence * (1 - prevalence)
        brier_skill = None if baseline_brier == 0.0 else 1 - brier / baseline_brier

        logits = tuple(_logit(pi) for pi in p)
        intercept, slope, cov00, _, cov11 = _fit_logistic_calibration(logits, y)
        intercept_se = sqrt(max(cov00, 0.0))
        slope_se = sqrt(max(cov11, 0.0))
        intercept_ci = (intercept - _Z95 * intercept_se, intercept + _Z95 * intercept_se)
        slope_ci = (slope - _Z95 * slope_se, slope + _Z95 * slope_se)

        expected = sum(p)
        observed = sum(y)
        observed_expected = None if expected <= 0 else observed / expected
        observed_expected_ci = None
        if observed > 0 and expected > 0:
            se_log = 1 / sqrt(observed)
            observed_expected_ci = (
                observed_expected * exp(-_Z95 * se_log),
                observed_expected * exp(_Z95 * se_log),
            )

        bin_errors: list[float] = []
        for index in range(bins):
            lower, upper = index / bins, (index + 1) / bins
            members = [
                i for i, pi in enumerate(p)
                if lower <= pi < upper or (index == bins - 1 and pi == 1.0)
            ]
            if members:
                bin_errors.append(sum(y[i] - p[i] for i in members) / len(members))

        return CalibrationReport(
            brier_score=brier,
            log_loss=log_loss,
            calibration_in_the_large=intercept,
            calibration_slope=slope,
            calibration_intercept_se=intercept_se,
            calibration_slope_se=slope_se,
            calibration_intercept_ci=intercept_ci,
            calibration_slope_ci=slope_ci,
            observed_expected_ratio=observed_expected,
            observed_expected_ratio_ci=observed_expected_ci,
            brier_skill_score=brier_skill,
            bin_errors=tuple(bin_errors),
            n=n,
            positive_rate=prevalence,
        )

    @staticmethod
    def discrimination(predictions: Sequence[float], outcomes: Sequence[int]) -> float | None:
        if len(predictions) != len(outcomes) or not predictions:
            raise ValueError("predictions and outcomes must be non-empty and have equal length")
        if any(o not in (0, 1) for o in outcomes):
            raise ValueError("binary outcomes must be 0 or 1")
        return _auc(predictions, outcomes)

    @staticmethod
    def prevalence_interval(outcomes: Sequence[int]) -> tuple[float, float]:
        if not outcomes or any(o not in (0, 1) for o in outcomes):
            raise ValueError("outcomes must be non-empty and binary")
        return _wilson_interval(sum(outcomes), len(outcomes))


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
    development_data_disjoint: bool = False
    bootstrap_or_cross_validation: bool = False
    horizon: str | None = None

    @property
    def externally_validated(self) -> bool:
        return self.validation_level in {ValidationLevel.EXTERNAL, ValidationLevel.PROSPECTIVE}

    @property
    def scientifically_strong(self) -> bool:
        return (
            self.externally_validated
            and self.temporal_holdout
            and self.development_data_disjoint
            and self.calibration is not None
            and self.calibration.calibration_intercept_ci is not None
            and self.calibration.calibration_slope_ci is not None
        )


__all__ = ["CalibrationReport", "Estimate", "MissingDataAssessment", "PredictiveValidation", "ValidationAssessment"]
