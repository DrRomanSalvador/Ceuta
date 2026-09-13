"""Operational scientific-assurance primitives for CeutIA.

These primitives translate the strongest methodological requirements in the
scientific evidence packages into deterministic, auditable controls. They do
not claim that a methodological standard is universally applicable: each
assessment records applicability and assumptions explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Mapping, Sequence


class GradeDomain(StrEnum):
    RISK_OF_BIAS = "risk_of_bias"
    INCONSISTENCY = "inconsistency"
    INDIRECTNESS = "indirectness"
    IMPRECISION = "imprecision"
    PUBLICATION_BIAS = "publication_bias"


class GradeRating(StrEnum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass(frozen=True, slots=True)
class GradeAssessment:
    """GRADE-style certainty assessment with explicit downgrading reasons.

    Ratings are deliberately represented as ordered categories rather than a
    pseudo-quantitative score. A domain is either assessed or explicitly
    marked unknown; the final certainty is the lowest supported level after
    downgrades.
    """

    initial: GradeRating
    risk_of_bias: GradeRating | None = None
    inconsistency: GradeRating | None = None
    indirectness: GradeRating | None = None
    imprecision: GradeRating | None = None
    publication_bias: GradeRating | None = None
    reasons: tuple[str, ...] = ()

    @property
    def certainty(self) -> GradeRating:
        rank = {GradeRating.HIGH: 3, GradeRating.MODERATE: 2, GradeRating.LOW: 1, GradeRating.VERY_LOW: 0}
        ratings = [self.initial]
        ratings.extend(x for x in (self.risk_of_bias, self.inconsistency, self.indirectness, self.imprecision, self.publication_bias) if x is not None)
        return min(ratings, key=lambda x: rank[x])

    @property
    def complete(self) -> bool:
        return all(x is not None for x in (self.risk_of_bias, self.inconsistency, self.indirectness, self.imprecision, self.publication_bias))


@dataclass(frozen=True, slots=True)
class SourceDependence:
    """Dependency-adjusted evidence identity.

    Sources sharing the same common-origin identifier are not counted as
    independent corroboration merely because they are separately published.
    """

    source_id: str
    common_origin_id: str
    evidence_id: str
    independence_weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.source_id or not self.common_origin_id or not self.evidence_id:
            raise ValueError("source and evidence identities are required")
        if not 0.0 <= self.independence_weight <= 1.0:
            raise ValueError("independence_weight must be in [0,1]")


class EvidenceDependenceAnalyzer:
    @staticmethod
    def effective_independent_weight(items: Sequence[SourceDependence]) -> float:
        """Return corroboration weight after collapsing common-origin sources."""
        by_origin: dict[str, float] = {}
        for item in items:
            by_origin[item.common_origin_id] = max(by_origin.get(item.common_origin_id, 0.0), item.independence_weight)
        return sum(by_origin.values())

    @staticmethod
    def duplicated_origins(items: Sequence[SourceDependence]) -> tuple[str, ...]:
        counts: dict[str, int] = {}
        for item in items:
            counts[item.common_origin_id] = counts.get(item.common_origin_id, 0) + 1
        return tuple(sorted(origin for origin, count in counts.items() if count > 1))


@dataclass(frozen=True, slots=True)
class CausalAssumptions:
    """Required assumptions for dynamic/causal policy reasoning."""

    exchangeability: bool
    positivity: bool
    consistency: bool
    interference: bool = False
    assumptions_documented: bool = True

    @property
    def decision_ready(self) -> bool:
        return self.assumptions_documented and self.exchangeability and self.positivity and self.consistency


@dataclass(frozen=True, slots=True)
class DriftAssessment:
    """Post-deployment dataset/model drift assessment."""

    baseline_reference: str
    current_reference: str
    covariate_shift: float | None = None
    calibration_drift: float | None = None
    outcome_rate_shift: float | None = None
    concept_drift: bool = False
    recalibration_performed: bool = False

    def __post_init__(self) -> None:
        for name in ("covariate_shift", "calibration_drift", "outcome_rate_shift"):
            value = getattr(self, name)
            if value is not None and (not isfinite(value) or value < 0.0):
                raise ValueError(f"{name} must be finite and non-negative")

    @property
    def requires_model_review(self) -> bool:
        return self.concept_drift or (self.calibration_drift is not None and self.calibration_drift > 0.0 and not self.recalibration_performed)


@dataclass(frozen=True, slots=True)
class EarlyWarningMetrics:
    """Outcome-based evaluation of an early-warning detector."""

    false_alarm_rate: float
    missed_event_rate: float
    detection_delay: float
    warning_lead_time: float | None = None

    def __post_init__(self) -> None:
        for name in ("false_alarm_rate", "missed_event_rate"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0 or not isfinite(value):
                raise ValueError(f"{name} must be finite and in [0,1]")
        if self.detection_delay < 0 or not isfinite(self.detection_delay):
            raise ValueError("detection_delay must be finite and non-negative")
        if self.warning_lead_time is not None and (self.warning_lead_time < 0 or not isfinite(self.warning_lead_time)):
            raise ValueError("warning_lead_time must be finite and non-negative")


class AssuranceDisposition(StrEnum):
    ALLOW = "allow"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class RuntimeSafetyAssessment:
    """Runtime-assurance result for a candidate decision."""

    safety_constraints_satisfied: bool
    independent_monitor_available: bool
    fallback_available: bool
    evidence_uncertainty: float
    decision_uncertainty: float

    @property
    def disposition(self) -> AssuranceDisposition:
        uncertainty = max(self.evidence_uncertainty, self.decision_uncertainty)
        if not self.safety_constraints_satisfied or not self.independent_monitor_available:
            return AssuranceDisposition.ABSTAIN
        if not self.fallback_available or uncertainty >= 0.75:
            return AssuranceDisposition.HUMAN_REVIEW
        return AssuranceDisposition.ALLOW


@dataclass(frozen=True, slots=True)
class CalibrationSlopeReport:
    slope: float
    intercept: float
    n: int


class CalibrationSlope:
    """Fits the standard logistic calibration model for binary predictions."""

    @staticmethod
    def fit(predictions: Sequence[float], outcomes: Sequence[int]) -> CalibrationSlopeReport:
        if len(predictions) != len(outcomes) or len(predictions) < 2:
            raise ValueError("predictions and outcomes must have equal length >= 2")
        if any(not 0.0 < float(p) < 1.0 for p in predictions):
            raise ValueError("calibration slope requires probabilities strictly between 0 and 1")
        if any(o not in (0, 1) for o in outcomes):
            raise ValueError("outcomes must be binary")
        xs = [__import__("math").log(float(p) / (1.0 - float(p))) for p in predictions]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(outcomes) / len(outcomes)
        variance = sum((x - mean_x) ** 2 for x in xs)
        if variance == 0.0:
            raise ValueError("calibration slope is undefined for constant predictions")
        covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, outcomes))
        slope = covariance / variance
        intercept = mean_y - slope * mean_x
        return CalibrationSlopeReport(slope=slope, intercept=intercept, n=len(predictions))


__all__ = [
    "AssuranceDisposition",
    "CalibrationSlope",
    "CalibrationSlopeReport",
    "CausalAssumptions",
    "DriftAssessment",
    "EarlyWarningMetrics",
    "EvidenceDependenceAnalyzer",
    "GradeAssessment",
    "GradeDomain",
    "GradeRating",
    "RuntimeSafetyAssessment",
    "SourceDependence",
]
