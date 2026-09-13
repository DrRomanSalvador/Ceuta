"""Validation primitives for predictive reliability and missing-data handling.

The module reports calibration quantities separately from discrimination and
never converts an AUC or accuracy value into a calibration claim. It also
keeps MCAR/MAR/MNAR assumptions explicit because missingness mechanism is a
causal/statistical assumption, not something that can be silently inferred.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .scientific_evidence import Missingness, ValidationLevel


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    brier_score: float
    calibration_in_the_large: float
    observed_expected_ratio: float | None
    bin_errors: tuple[float, ...]
    n: int
    method: str = "binary_outcome_calibration"

    @property
    def mean_absolute_bin_error(self) -> float:
        return sum(abs(x) for x in self.bin_errors) / len(self.bin_errors) if self.bin_errors else 0.0


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
        observed_rate = sum(outcomes) / n
        predicted_rate = sum(predictions) / n
        brier = sum((float(p) - o) ** 2 for p, o in zip(predictions, outcomes)) / n
        calibration_in_large = predicted_rate - observed_rate
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
        return CalibrationReport(brier, calibration_in_large, observed_expected, tuple(errors), n)


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
