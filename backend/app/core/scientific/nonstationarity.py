"""Non-stationarity controls for crisis forecasting under changing DGPs.

The module does not assume stationarity. It detects observable distribution/regime
shifts, structural breaks and deployment values outside the declared reference
support. These are epistemic risk signals, not proofs that a causal regime
change occurred. Forecasts are therefore downgraded or blocked when support is
not demonstrated.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import sqlite3
from statistics import mean, pvariance
from typing import Sequence


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class RegimeObservation:
    observed_at: datetime
    value: float
    reference_min: float
    reference_max: float
    source_id: str
    provenance_ref: str

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if not all(math.isfinite(x) for x in (self.value, self.reference_min, self.reference_max)):
            raise ValueError("observation values must be finite")
        if self.reference_min > self.reference_max:
            raise ValueError("reference_min cannot exceed reference_max")
        if not self.source_id or not self.provenance_ref:
            raise ValueError("source_id and provenance_ref are required")


@dataclass(frozen=True, slots=True)
class NonStationarityAssessment:
    state: str
    distribution_shift: bool
    structural_break: bool
    extrapolation: bool
    regime_change: bool
    uncertainty: float
    reasons: tuple[str, ...]
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        if self.state not in {"stable", "review", "abstain"}:
            raise ValueError("invalid non-stationarity state")
        if not 0.0 <= self.uncertainty <= 1.0 or not math.isfinite(self.uncertainty):
            raise ValueError("uncertainty must be in [0,1]")
        if not self.reasons or not self.evidence_fingerprint:
            raise ValueError("assessment must be auditable")


class NonStationarityMonitor:
    """Detects regime instability without pretending to identify its cause."""

    RULE_VERSION = "nonstationarity-v1"

    def __init__(self, storage_path: str, *, window: int = 8, mean_shift: float = 0.25,
                 variance_ratio: float = 2.0) -> None:
        if not storage_path or window < 4 or mean_shift <= 0 or variance_ratio <= 1:
            raise ValueError("invalid non-stationarity configuration")
        self.storage_path = storage_path
        self.window = window
        self.mean_shift = mean_shift
        self.variance_ratio = variance_ratio
        with sqlite3.connect(storage_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS nonstationarity_assessments(
                assessment_id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
                state TEXT NOT NULL, payload TEXT NOT NULL, evidence_fingerprint TEXT NOT NULL,
                rule_version TEXT NOT NULL)""")

    def assess(self, observations: Sequence[RegimeObservation], *, deployment_value: float | None = None) -> NonStationarityAssessment:
        if len(observations) < self.window * 2:
            raise ValueError("insufficient observations for regime comparison")
        ordered = tuple(sorted(observations, key=lambda x: x.observed_at))
        prior = [x.value for x in ordered[-2 * self.window:-self.window]]
        recent = [x.value for x in ordered[-self.window:]]
        prior_mean, recent_mean = mean(prior), mean(recent)
        prior_var, recent_var = pvariance(prior), pvariance(recent)
        scale = max(math.sqrt(prior_var), 1e-9)
        distribution_shift = abs(recent_mean - prior_mean) / scale >= self.mean_shift
        structural_break = recent_var / max(prior_var, 1e-9) >= self.variance_ratio or recent_var / max(prior_var, 1e-9) <= 1 / self.variance_ratio
        regime_change = distribution_shift or structural_break
        extrapolation = False
        if deployment_value is not None:
            bounds = [(x.reference_min, x.reference_max) for x in ordered]
            low, high = max(x[0] for x in bounds), min(x[1] for x in bounds)
            extrapolation = deployment_value < low or deployment_value > high
        reasons: list[str] = []
        if distribution_shift: reasons.append("distribution_shift")
        if structural_break: reasons.append("structural_break")
        if extrapolation: reasons.append("deployment_outside_reference_support")
        if not reasons: reasons.append("support_within_observed_reference")
        uncertainty = min(1.0, 0.35 * distribution_shift + 0.35 * structural_break + 0.5 * extrapolation)
        state = "abstain" if extrapolation else ("review" if regime_change else "stable")
        fingerprint = _digest([(x.observed_at.isoformat(), x.value, x.reference_min, x.reference_max, x.source_id, x.provenance_ref) for x in ordered])
        assessment = NonStationarityAssessment(state, distribution_shift, structural_break, extrapolation, regime_change, uncertainty, tuple(reasons), fingerprint)
        created = datetime.now(timezone.utc).isoformat()
        assessment_id = _digest((created, assessment.evidence_fingerprint, self.RULE_VERSION))
        payload = json.dumps({"state": assessment.state, "distribution_shift": assessment.distribution_shift, "structural_break": assessment.structural_break, "extrapolation": assessment.extrapolation, "regime_change": assessment.regime_change, "uncertainty": assessment.uncertainty, "reasons": assessment.reasons}, sort_keys=True, separators=(",", ":"))
        with sqlite3.connect(self.storage_path) as db:
            db.execute("INSERT INTO nonstationarity_assessments VALUES(?,?,?,?,?,?)", (assessment_id, created, assessment.state, payload, assessment.evidence_fingerprint, self.RULE_VERSION))
        return assessment

    def verify_integrity(self) -> bool:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT assessment_id,created_at,state,payload,evidence_fingerprint,rule_version FROM nonstationarity_assessments")
            for assessment_id, created, state, payload, fingerprint, rule_version in rows:
                if _digest((created, fingerprint, rule_version)) != assessment_id:
                    return False
                data = json.loads(payload)
                if data["state"] != state:
                    return False
        return True
