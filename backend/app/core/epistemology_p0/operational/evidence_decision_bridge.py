"""Operational bridge from evidence state to client-facing facts and decisions.

This module keeps observed facts, derived values, estimates and forecasts
explicitly separated. Missing/stale current values may be estimated only when
a deterministic statistical projection can be constructed from supplied
observations; the result retains its uncertainty and epistemic status.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from math import exp, isfinite, sqrt
from typing import Sequence


class EpistemicStatus(StrEnum):
    OBSERVED = "observed"
    REPORTED = "reported"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    FORECAST = "forecast"
    INFERRED = "inferred"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    source_id: str
    observed_at: datetime
    quality: float
    directness: float = 1.0
    relevance: float = 1.0
    independence_weight: float = 1.0
    epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.source_id:
            raise ValueError("evidence identity is required")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        for name in ("quality", "directness", "relevance", "independence_weight"):
            value = getattr(self, name)
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0,1]")

    def weight(self, *, as_of: datetime, half_life_days: float) -> float:
        if as_of.tzinfo is None or half_life_days <= 0:
            raise ValueError("as_of must be timezone-aware and half_life_days positive")
        age_days = max(0.0, (as_of - self.observed_at).total_seconds() / 86400.0)
        freshness = exp(-age_days * 0.6931471805599453 / half_life_days)
        return self.quality * self.directness * self.relevance * self.independence_weight * freshness


@dataclass(frozen=True, slots=True)
class ClientValue:
    value: float | None
    status: EpistemicStatus
    as_of: datetime
    interval_lower: float | None
    interval_upper: float | None
    interval_confidence: float | None
    method: str
    evidence_refs: tuple[str, ...]
    uncertainty: float

    @property
    def is_observation(self) -> bool:
        return self.status in {EpistemicStatus.OBSERVED, EpistemicStatus.REPORTED}


@dataclass(frozen=True, slots=True)
class _Point:
    at: datetime
    value: float
    weight: float
    evidence_id: str


class EvidenceDecisionBridge:
    """Converts evidence into auditable client values and decision inputs."""

    def resolve_current_value(
        self,
        *,
        observations: Sequence[tuple[datetime, float, str]],
        evidence: Sequence[EvidenceRecord],
        as_of: datetime,
        half_life_days: float,
        allow_estimation: bool = True,
    ) -> ClientValue:
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        if not observations:
            return ClientValue(None, EpistemicStatus.INSUFFICIENT_EVIDENCE, as_of, None, None, None, "no_observation", 1.0, tuple())

        evidence_by_id = {item.evidence_id: item for item in evidence}
        points: list[_Point] = []
        for at, value, evidence_id in observations:
            if at.tzinfo is None or not isfinite(value):
                raise ValueError("observation timestamps must be timezone-aware and values finite")
            record = evidence_by_id.get(evidence_id)
            if record is None:
                raise ValueError(f"missing evidence record: {evidence_id}")
            points.append(_Point(at, value, record.weight(as_of=as_of, half_life_days=half_life_days), evidence_id))

        points.sort(key=lambda item: item.at)
        latest = points[-1]
        age_days = max(0.0, (as_of - latest.at).total_seconds() / 86400.0)
        if age_days == 0.0:
            return ClientValue(latest.value, EpistemicStatus.OBSERVED, as_of, latest.value, latest.value, 1.0, "direct_observation", (latest.evidence_id,), 0.0)
        if not allow_estimation or len(points) < 3:
            return ClientValue(None, EpistemicStatus.INSUFFICIENT_EVIDENCE, as_of, None, None, None, "stale_observation_without_estimable_series", tuple(p.evidence_id for p in points), 1.0)

        return self._weighted_linear_projection(points, as_of)

    @staticmethod
    def _weighted_linear_projection(points: Sequence[_Point], target: datetime) -> ClientValue:
        origin = points[0].at
        x = [(p.at - origin).total_seconds() / 86400.0 for p in points]
        xt = (target - origin).total_seconds() / 86400.0
        weights = [max(p.weight, 1e-12) for p in points]
        total_w = sum(weights)
        xbar = sum(w * value for w, value in zip(weights, x)) / total_w
        ybar = sum(w * p.value for w, p in zip(weights, points)) / total_w
        sxx = sum(w * (value - xbar) ** 2 for w, value in zip(weights, x))
        if sxx <= 0.0:
            return ClientValue(None, EpistemicStatus.INSUFFICIENT_EVIDENCE, target, None, None, None, "no_temporal_variation", tuple(p.evidence_id for p in points), 1.0)
        slope = sum(w * (xi - xbar) * (p.value - ybar) for w, xi, p in zip(weights, x, points)) / sxx
        intercept = ybar - slope * xbar
        estimate = intercept + slope * xt
        residual_ss = sum(w * (p.value - (intercept + slope * xi)) ** 2 for w, xi, p in zip(weights, x, points))
        dof = max(1.0, total_w - 2.0)
        residual_var = residual_ss / dof
        leverage = (1.0 / total_w) + ((xt - xbar) ** 2 / sxx)
        prediction_se = sqrt(max(0.0, residual_var * (1.0 + leverage)))
        half_width = 1.96 * prediction_se
        confidence = 0.95
        uncertainty = min(1.0, half_width / max(abs(estimate), 1e-12))
        return ClientValue(
            estimate,
            EpistemicStatus.ESTIMATED,
            target,
            estimate - half_width,
            estimate + half_width,
            confidence,
            "weighted_linear_projection_normal_approximation",
            tuple(p.evidence_id for p in points),
            uncertainty,
        )

    @staticmethod
    def combine_decision_uncertainty(option_uncertainty: float, epistemic_uncertainty: float) -> float:
        if not 0.0 <= option_uncertainty <= 1.0 or not 0.0 <= epistemic_uncertainty <= 1.0:
            raise ValueError("uncertainty values must be in [0,1]")
        return max(option_uncertainty, epistemic_uncertainty)


__all__ = ["ClientValue", "EpistemicStatus", "EvidenceDecisionBridge", "EvidenceRecord"]
