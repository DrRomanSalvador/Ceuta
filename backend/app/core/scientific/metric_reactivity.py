"""Goodhart-aware metric governance and reflexive measurement control.

CeutIA must assume that indicators become endogenous once they influence
resource allocation, alerts, reputation or intervention. This module therefore
tracks indicator exposure, tests for observable gaming signatures, rotates
indicator roles, and records intervention feedback against outcomes rather than
assuming the metric remains a stationary proxy for the latent phenomenon.

The detectors are *signals of possible corruption*, not proof of misconduct.
They fail closed by degrading indicator validity and raising governance review.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
from math import isfinite
from statistics import fmean
from typing import Sequence


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class IndicatorSpec:
    indicator_id: str
    version: str
    mechanism: str
    targetable: bool
    rotation_group: str
    causal_anchor: str = ""

    def __post_init__(self) -> None:
        if not self.indicator_id or not self.version or not self.mechanism or not self.rotation_group:
            raise ValueError("indicator identity, mechanism and rotation group are required")
        if self.targetable and not self.causal_anchor:
            # Targetability without a causal anchor is especially vulnerable to
            # measure fixation and must not be released as a primary indicator.
            raise ValueError("targetable indicators require an explicit causal anchor")


@dataclass(frozen=True, slots=True)
class IndicatorObservation:
    indicator_id: str
    value: float
    observed_at: datetime
    source_ref: str
    exposed: bool

    def __post_init__(self) -> None:
        if not self.indicator_id or not self.source_ref or not isfinite(self.value):
            raise ValueError("valid indicator observation is required")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class GamingDiagnostics:
    observation_count: int
    threshold_discontinuity: float
    missingness_shift: float
    cross_source_divergence: float
    outcome_decoupling: float
    exposure_duration: int
    corruption_score: float
    flags: tuple[str, ...]
    validity: float

    @property
    def requires_review(self) -> bool:
        return bool(self.flags)


class MetricReactivityMonitor:
    """Persistent monitor for endogenous metric corruption.

    No single statistical pattern proves gaming. The score combines independent
    diagnostics and is deliberately bounded. Exposure duration is itself a
    risk factor: an indicator under control pressure is not assumed to remain
    valid merely because its historical predictive relationship was strong.
    """

    VERSION = "metric-reactivity-v1"

    def __init__(self, *, storage_path: str | None = None, review_threshold: float = 0.45,
                 abstain_threshold: float = 0.75, max_exposure_observations: int = 20) -> None:
        if not 0 <= review_threshold < abstain_threshold <= 1:
            raise ValueError("invalid corruption thresholds")
        if max_exposure_observations < 1:
            raise ValueError("max_exposure_observations must be positive")
        self.storage_path = storage_path
        self.review_threshold = review_threshold
        self.abstain_threshold = abstain_threshold
        self.max_exposure_observations = max_exposure_observations
        self._specs: dict[str, IndicatorSpec] = {}
        self._observations: list[IndicatorObservation] = []
        self._interventions: dict[str, tuple[str, str, datetime]] = {}
        if storage_path:
            self._init_db(); self._load_db()

    def _db(self) -> sqlite3.Connection:
        if not self.storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self.storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS indicator_specs(indicator_id TEXT PRIMARY KEY, payload TEXT NOT NULL, record_hash TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS indicator_observations(id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT NOT NULL, record_hash TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS metric_interventions(intervention_id TEXT PRIMARY KEY, indicator_id TEXT NOT NULL, action TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL)")

    def _load_db(self) -> None:
        with self._db() as db:
            for indicator_id, payload, record_hash in db.execute("SELECT indicator_id,payload,record_hash FROM indicator_specs"):
                if _digest(json.loads(payload)) != record_hash:
                    raise ValueError("indicator specification integrity failure")
                p = json.loads(payload)
                self._specs[indicator_id] = IndicatorSpec(**p)
            for payload, record_hash in db.execute("SELECT payload,record_hash FROM indicator_observations ORDER BY id"):
                if _digest(json.loads(payload)) != record_hash:
                    raise ValueError("indicator observation integrity failure")
                p = json.loads(payload)
                self._observations.append(IndicatorObservation(p["indicator_id"], p["value"], datetime.fromisoformat(p["observed_at"]), p["source_ref"], p["exposed"]))

    def register(self, spec: IndicatorSpec) -> None:
        existing = self._specs.get(spec.indicator_id)
        if existing and existing != spec:
            raise ValueError("indicator specification is immutable; create a new indicator_id/version")
        self._specs[spec.indicator_id] = spec
        if self.storage_path and existing is None:
            payload = {"indicator_id": spec.indicator_id, "version": spec.version, "mechanism": spec.mechanism, "targetable": spec.targetable, "rotation_group": spec.rotation_group, "causal_anchor": spec.causal_anchor}
            with self._db() as db:
                db.execute("INSERT INTO indicator_specs VALUES(?,?,?)", (spec.indicator_id, _canonical(payload), _digest(payload)))

    def observe(self, observation: IndicatorObservation) -> None:
        if observation.indicator_id not in self._specs:
            raise ValueError("indicator must be registered before observation")
        self._observations.append(observation)
        if self.storage_path:
            payload = {"indicator_id": observation.indicator_id, "value": observation.value, "observed_at": observation.observed_at.isoformat(), "source_ref": observation.source_ref, "exposed": observation.exposed}
            with self._db() as db:
                db.execute("INSERT INTO indicator_observations(payload,record_hash) VALUES(?,?)", (_canonical(payload), _digest(payload)))

    def record_intervention(self, intervention_id: str, indicator_id: str, action: str, *, created_at: datetime | None = None) -> None:
        if not intervention_id or indicator_id not in self._specs or not action:
            raise ValueError("intervention identity, indicator and action are required")
        created_at = created_at or datetime.now(timezone.utc)
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        if intervention_id in self._interventions:
            raise ValueError("duplicate intervention")
        self._interventions[intervention_id] = (indicator_id, action, created_at)
        if self.storage_path:
            payload = {"intervention_id": intervention_id, "indicator_id": indicator_id, "action": action, "created_at": created_at.isoformat()}
            with self._db() as db:
                db.execute("INSERT INTO metric_interventions VALUES(?,?,?,?,?)", (intervention_id, indicator_id, action, created_at.isoformat(), _canonical(payload)))

    @staticmethod
    def _threshold_discontinuity(values: Sequence[float]) -> float:
        if len(values) < 6:
            return 0.0
        ordered = sorted(values)
        mid = len(ordered) // 2
        left, right = ordered[:mid], ordered[mid:]
        return min(1.0, abs(fmean(right) - fmean(left)) / (abs(fmean(values)) + 1e-9))

    @staticmethod
    def _missingness_shift(observations: Sequence[IndicatorObservation]) -> float:
        if len(observations) < 6:
            return 0.0
        midpoint = len(observations) // 2
        before = observations[:midpoint]
        after = observations[midpoint:]
        # Observations are present records; missingness is inferred only from
        # explicit source discontinuity, never invented from absent timestamps.
        before_sources = {x.source_ref for x in before}
        after_sources = {x.source_ref for x in after}
        return 1.0 if before_sources and after_sources and before_sources.isdisjoint(after_sources) else 0.0

    @staticmethod
    def _cross_source_divergence(observations: Sequence[IndicatorObservation]) -> float:
        by_source: dict[str, list[float]] = {}
        for x in observations:
            by_source.setdefault(x.source_ref, []).append(x.value)
        means = [fmean(v) for v in by_source.values() if v]
        if len(means) < 2:
            return 0.0
        return min(1.0, (max(means) - min(means)) / (abs(fmean(means)) + 1e-9))

    @staticmethod
    def _outcome_decoupling(values: Sequence[float], outcomes: Sequence[float] | None) -> float:
        if outcomes is None or len(values) != len(outcomes) or len(values) < 4:
            return 0.0
        vx = max(values) - min(values)
        vy = max(outcomes) - min(outcomes)
        if vx == 0 or vy == 0:
            return 0.0
        # A large change in the metric with almost no corresponding outcome
        # movement is a bounded decoupling signal, not proof of gaming.
        ratio = abs(fmean(values) - values[0]) / (abs(fmean(values)) + 1e-9)
        outcome_ratio = abs(fmean(outcomes) - outcomes[0]) / (abs(fmean(outcomes)) + 1e-9)
        return min(1.0, max(0.0, ratio - outcome_ratio))

    def diagnose(self, indicator_id: str, *, outcomes: Sequence[float] | None = None) -> GamingDiagnostics:
        if indicator_id not in self._specs:
            raise KeyError(indicator_id)
        observations = tuple(x for x in self._observations if x.indicator_id == indicator_id)
        values = tuple(x.value for x in observations)
        spec = self._specs[indicator_id]
        exposure_duration = sum(x.exposed for x in observations)
        threshold = self._threshold_discontinuity(values)
        missingness = self._missingness_shift(observations)
        divergence = self._cross_source_divergence(observations)
        decoupling = self._outcome_decoupling(values, outcomes)
        exposure_risk = min(1.0, exposure_duration / self.max_exposure_observations)
        corruption = min(1.0, 0.30 * threshold + 0.15 * missingness + 0.25 * divergence + 0.20 * decoupling + 0.10 * exposure_risk)
        flags: list[str] = []
        if threshold >= 0.45:
            flags.append("distribution_or_threshold_anomaly")
        if missingness >= 0.5:
            flags.append("source_availability_shift")
        if divergence >= 0.45:
            flags.append("cross_source_divergence")
        if decoupling >= 0.45:
            flags.append("indicator_outcome_decoupling")
        if spec.targetable and exposure_duration >= self.max_exposure_observations:
            flags.append("prolonged_control_exposure")
        validity = max(0.0, 1.0 - corruption)
        if corruption >= self.abstain_threshold:
            flags.append("indicator_validity_compromised")
        elif corruption >= self.review_threshold:
            flags.append("indicator_requires_review")
        return GamingDiagnostics(len(observations), threshold, missingness, divergence, decoupling, exposure_duration, corruption, tuple(dict.fromkeys(flags)), validity)

    def rotate(self, indicator_id: str, *, replacement_id: str) -> tuple[str, str]:
        if indicator_id not in self._specs or replacement_id not in self._specs:
            raise KeyError("indicator must be registered before rotation")
        old, new = self._specs[indicator_id], self._specs[replacement_id]
        if old.rotation_group != new.rotation_group:
            raise ValueError("rotation requires the same rotation group")
        if old.indicator_id == new.indicator_id:
            raise ValueError("replacement must differ")
        return old.indicator_id, new.indicator_id

    def governance_state(self, indicator_id: str, *, outcomes: Sequence[float] | None = None) -> tuple[bool, float, int, str]:
        diagnostics = self.diagnose(indicator_id, outcomes=outcomes)
        if "indicator_validity_compromised" in diagnostics.flags:
            return False, diagnostics.validity, 1, "abstain"
        if diagnostics.requires_review:
            return True, diagnostics.validity, 1, "review_required"
        return True, diagnostics.validity, 0, "release"


@dataclass(frozen=True, slots=True)
class ReflexiveInterventionOutcome:
    intervention_id: str
    indicator_id: str
    outcome_reference: str
    indicator_change: float
    underlying_outcome_change: float
    observed_at: datetime

    def __post_init__(self) -> None:
        if not self.intervention_id or not self.indicator_id or not self.outcome_reference:
            raise ValueError("intervention outcome references are required")
        if any(not isfinite(x) for x in (self.indicator_change, self.underlying_outcome_change)):
            raise ValueError("intervention changes must be finite")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")


__all__ = ["IndicatorSpec", "IndicatorObservation", "GamingDiagnostics", "MetricReactivityMonitor", "ReflexiveInterventionOutcome"]
