"""Evidence-bounded early-warning governance.

This module turns four scientifically distinct concerns into auditable state:

* credibility loss from false alarms (cry-wolf / preparedness decay),
* critical-slowing-down diagnostics with explicit data sufficiency limits,
* prediction-market observations as benchmark/ensemble evidence rather than
  causal explanations, and
* vulnerability/root-cause context so hazard probability is not mistaken for
  social risk.

None of these signals is treated as proof of a tipping point, misconduct, or
causal effect. The assessment is deliberately fail-closed when the required
measurement contract is not satisfied.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
from math import isfinite
from statistics import fmean, pvariance
from typing import Sequence



def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class CryWolfPolicy:
    """Asymmetric credibility policy.

    The asymmetry is a configurable governance assumption, not an empirical
    constant. It must be validated prospectively for the deployed population.
    """

    false_alarm_penalty: float = 2.0
    correct_warning_reward: float = 1.0
    missed_warning_penalty: float = 1.0
    minimum_observations: int = 5
    abstain_trust: float = 0.35
    review_trust: float = 0.55

    def __post_init__(self) -> None:
        values = (self.false_alarm_penalty, self.correct_warning_reward, self.missed_warning_penalty, self.abstain_trust, self.review_trust)
        if any(not isfinite(v) or v <= 0 for v in values):
            raise ValueError("cry-wolf policy values must be positive and finite")
        if self.false_alarm_penalty <= self.correct_warning_reward:
            raise ValueError("false-alarm penalty must exceed correct-warning reward")
        if not 1 <= self.minimum_observations:
            raise ValueError("minimum_observations must be positive")
        if self.abstain_trust >= self.review_trust or self.review_trust > 1:
            raise ValueError("trust thresholds must satisfy abstain < review <= 1")


@dataclass(frozen=True, slots=True)
class WarningOutcome:
    warning_id: str
    issued: bool
    event_occurred: bool
    observed_at: datetime

    def __post_init__(self) -> None:
        if not self.warning_id:
            raise ValueError("warning_id is required")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")

    @property
    def false_alarm(self) -> bool:
        return self.issued and not self.event_occurred

    @property
    def correct_warning(self) -> bool:
        return self.issued and self.event_occurred

    @property
    def missed_warning(self) -> bool:
        return not self.issued and self.event_occurred


@dataclass(frozen=True, slots=True)
class CredibilityState:
    observations: int
    false_alarms: int
    correct_warnings: int
    missed_warnings: int
    trust: float
    preparedness: float
    policy_version: str


class CryWolfTracker:
    """Durable credibility state derived from settled warning outcomes."""

    POLICY_VERSION = "cry-wolf-v1"

    def __init__(self, policy: CryWolfPolicy | None = None, *, storage_path: str | None = None) -> None:
        self.policy = policy or CryWolfPolicy()
        self.storage_path = storage_path
        self._outcomes: dict[str, WarningOutcome] = {}
        if storage_path:
            self._init_db()
            self._load_db()

    def _db(self) -> sqlite3.Connection:
        if not self.storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self.storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS cry_wolf_outcomes(warning_id TEXT PRIMARY KEY, issued INTEGER NOT NULL, event_occurred INTEGER NOT NULL, observed_at TEXT NOT NULL)")

    def _load_db(self) -> None:
        with self._db() as db:
            for row in db.execute("SELECT warning_id,issued,event_occurred,observed_at FROM cry_wolf_outcomes"):
                self._outcomes[row[0]] = WarningOutcome(row[0], bool(row[1]), bool(row[2]), datetime.fromisoformat(row[3]))

    def record(self, outcome: WarningOutcome) -> None:
        if outcome.warning_id in self._outcomes:
            raise ValueError("duplicate warning outcome")
        self._outcomes[outcome.warning_id] = outcome
        if self.storage_path:
            with self._db() as db:
                db.execute("INSERT INTO cry_wolf_outcomes VALUES(?,?,?,?)", (outcome.warning_id, int(outcome.issued), int(outcome.event_occurred), outcome.observed_at.isoformat()))

    def state(self) -> CredibilityState:
        xs = tuple(self._outcomes.values())
        false_alarms = sum(x.false_alarm for x in xs)
        correct = sum(x.correct_warning for x in xs)
        missed = sum(x.missed_warning for x in xs)
        n = len(xs)
        # Bounded credibility/preparedness state.  The weights are intentionally
        # not presented as universal behavioral constants.
        total = self.policy.correct_warning_reward * correct + self.policy.false_alarm_penalty * false_alarms + self.policy.missed_warning_penalty * missed
        trust = (self.policy.correct_warning_reward * correct + 0.5 * self.policy.false_alarm_penalty * 0 + 1.0) / (total + 1.0)
        preparedness = (self.policy.correct_warning_reward * correct + 1.0) / (self.policy.correct_warning_reward * correct + self.policy.false_alarm_penalty * false_alarms + self.policy.missed_warning_penalty * missed + 1.0)
        return CredibilityState(n, false_alarms, correct, missed, min(1.0, trust), min(1.0, preparedness), self.POLICY_VERSION)

    def disposition(self) -> str:
        state = self.state()
        if state.observations < self.policy.minimum_observations:
            return "review_required"
        if state.trust < self.policy.abstain_trust:
            return "abstain"
        if state.trust < self.policy.review_trust:
            return "review_required"
        return "release"


@dataclass(frozen=True, slots=True)
class CriticalSlowingDownSignal:
    observations: int
    variance: float
    lag1_autocorrelation: float
    sufficient_data: bool
    confounders_present: bool
    interpretation: str

    @property
    def usable_as_supporting_signal(self) -> bool:
        return self.sufficient_data and not self.confounders_present


class CriticalSlowingDown:
    """Conservative variance/autocorrelation diagnostic.

    This estimates a statistical signature; it does not infer a tipping point
    without a domain-specific dynamical model and confounder controls.
    """

    def __init__(self, *, minimum_observations: int = 30) -> None:
        if minimum_observations < 3:
            raise ValueError("minimum_observations must be >= 3")
        self.minimum_observations = minimum_observations

    def evaluate(self, values: Sequence[float], *, confounders_present: bool = False) -> CriticalSlowingDownSignal:
        xs = tuple(float(x) for x in values)
        if any(not isfinite(x) for x in xs):
            raise ValueError("critical-slowing-down series must be finite")
        n = len(xs)
        if n < 2:
            raise ValueError("at least two observations are required")
        mean = fmean(xs)
        variance = pvariance(xs) if n > 1 else 0.0
        denom = sum((x - mean) ** 2 for x in xs)
        lag1 = sum((xs[i] - mean) * (xs[i - 1] - mean) for i in range(1, n)) / denom if denom > 0 else 0.0
        sufficient = n >= self.minimum_observations
        if not sufficient:
            interpretation = "insufficient_data"
        elif confounders_present:
            interpretation = "confounded_do_not_release"
        else:
            interpretation = "supporting_resilience_diagnostic"
        return CriticalSlowingDownSignal(n, variance, lag1, sufficient, confounders_present, interpretation)


@dataclass(frozen=True, slots=True)
class PredictionMarketObservation:
    market_id: str
    probability: float
    liquidity_score: float
    integrity_valid: bool
    observed_at: datetime

    def __post_init__(self) -> None:
        if not self.market_id or not isfinite(self.probability) or not 0 <= self.probability <= 1:
            raise ValueError("invalid market observation")
        if not isfinite(self.liquidity_score) or not 0 <= self.liquidity_score <= 1:
            raise ValueError("liquidity_score must be in [0,1]")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")

    @property
    def usable_as_benchmark(self) -> bool:
        return self.integrity_valid and self.liquidity_score > 0


@dataclass(frozen=True, slots=True)
class VulnerabilityProfile:
    exposure: float
    susceptibility: float
    coping_capacity: float
    structural_drivers: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not isfinite(x) or not 0 <= x <= 1 for x in (self.exposure, self.susceptibility, self.coping_capacity)):
            raise ValueError("vulnerability dimensions must be in [0,1]")
        if not self.structural_drivers:
            raise ValueError("structural drivers are required")

    @property
    def vulnerability_score(self) -> float:
        return min(1.0, self.exposure * self.susceptibility * (1.0 - self.coping_capacity))


@dataclass(frozen=True, slots=True)
class EarlyWarningAssessment:
    assessment_id: str
    cry_wolf: CredibilityState
    cry_wolf_disposition: str
    slowing_down: CriticalSlowingDownSignal
    market_benchmarks: tuple[PredictionMarketObservation, ...]
    vulnerability: VulnerabilityProfile
    alert_allowed: bool
    reasons: tuple[str, ...]
    created_at: datetime
    input_fingerprint: str


class EarlyWarningGovernance:
    """Combines the four constraints without turning them into false certainty."""

    def __init__(self, tracker: CryWolfTracker, *, storage_path: str | None = None) -> None:
        self.tracker = tracker
        self.storage_path = storage_path or tracker.storage_path
        if self.storage_path:
            with self._db() as db:
                db.execute("CREATE TABLE IF NOT EXISTS early_warning_assessments(assessment_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")

    def _db(self) -> sqlite3.Connection:
        if not self.storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self.storage_path)

    def assess(self, *, values: Sequence[float], vulnerability: VulnerabilityProfile, markets: Sequence[PredictionMarketObservation] = (), confounders_present: bool = False, now: datetime | None = None) -> EarlyWarningAssessment:
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        cry = self.tracker.state()
        cry_disposition = self.tracker.disposition()
        slowing = CriticalSlowingDown().evaluate(values, confounders_present=confounders_present)
        reasons: list[str] = []
        if cry_disposition == "abstain":
            reasons.append("cry_wolf_credibility_below_abstain_threshold")
        elif cry_disposition == "review_required":
            reasons.append("cry_wolf_requires_review")
        if not slowing.sufficient_data:
            reasons.append("critical_slowing_down_insufficient_data")
        if confounders_present:
            reasons.append("critical_slowing_down_confounders_present")
        if not any(m.usable_as_benchmark for m in markets):
            reasons.append("no_usable_prediction_market_benchmark")
        if vulnerability.vulnerability_score > 0.5:
            reasons.append("high_vulnerability_requires_targeted_response_design")
        alert_allowed = cry_disposition == "release" and slowing.usable_as_supporting_signal and vulnerability.vulnerability_score <= 0.8
        fingerprint = _digest({"cry": cry, "slowing": slowing, "markets": markets, "vulnerability": vulnerability})
        assessment = EarlyWarningAssessment(_digest((fingerprint, now.isoformat())), cry, cry_disposition, slowing, tuple(markets), vulnerability, alert_allowed, tuple(reasons), now, fingerprint)
        if self.storage_path:
            payload = {"assessment_id": assessment.assessment_id, "cry_wolf": assessment.cry_wolf, "cry_wolf_disposition": assessment.cry_wolf_disposition, "slowing_down": assessment.slowing_down, "market_benchmarks": assessment.market_benchmarks, "vulnerability": assessment.vulnerability, "alert_allowed": assessment.alert_allowed, "reasons": assessment.reasons, "created_at": assessment.created_at.isoformat(), "input_fingerprint": assessment.input_fingerprint}
            with self._db() as db:
                db.execute("INSERT INTO early_warning_assessments VALUES(?,?)", (assessment.assessment_id, _canonical(payload)))
        return assessment


__all__ = [
    "CryWolfPolicy", "WarningOutcome", "CredibilityState", "CryWolfTracker",
    "CriticalSlowingDownSignal", "CriticalSlowingDown", "PredictionMarketObservation",
    "VulnerabilityProfile", "EarlyWarningAssessment", "EarlyWarningGovernance",
]
