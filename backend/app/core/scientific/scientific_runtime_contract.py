"""Cross-cutting scientific runtime contracts.

This module turns previously disconnected epistemic constraints into a single,
durable runtime assessment. It is deliberately conservative: reference-class
support, observed-range support, causal identification and robust strategy
criteria are explicit inputs, never inferred from labels or documentation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
import math
import sqlite3


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


class RuntimeState(StrEnum):
    RELEASE = "release"
    REVIEW = "review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class ReferenceClassAssessment:
    reference_class_id: str
    sample_size: int
    minimum_sample_size: int
    support_score: float
    applicability_score: float
    unique_event: bool = False

    def __post_init__(self) -> None:
        if not self.reference_class_id.strip():
            raise ValueError("reference_class_id is required")
        if self.sample_size < 0 or self.minimum_sample_size < 1:
            raise ValueError("reference-class sample sizes are invalid")
        for value in (self.support_score, self.applicability_score):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("reference-class scores must be in [0,1]")

    @property
    def state(self) -> RuntimeState:
        if self.unique_event and self.sample_size < self.minimum_sample_size:
            return RuntimeState.ABSTAIN
        if self.support_score < 0.5 or self.applicability_score < 0.5:
            return RuntimeState.REVIEW
        return RuntimeState.RELEASE


@dataclass(frozen=True, slots=True)
class FeatureSupport:
    feature: str
    observed_min: float
    observed_max: float
    deployment_value: float
    review_margin: float = 0.05

    def __post_init__(self) -> None:
        if not self.feature.strip() or not all(math.isfinite(v) for v in (
            self.observed_min, self.observed_max, self.deployment_value, self.review_margin
        )):
            raise ValueError("feature support values must be finite")
        if self.observed_max <= self.observed_min:
            raise ValueError("observed support must have positive width")
        if self.review_margin < 0:
            raise ValueError("review_margin must be non-negative")

    @property
    def normalized_distance(self) -> float:
        width = self.observed_max - self.observed_min
        if self.deployment_value < self.observed_min:
            return (self.observed_min - self.deployment_value) / width
        if self.deployment_value > self.observed_max:
            return (self.deployment_value - self.observed_max) / width
        return 0.0

    @property
    def extrapolation(self) -> bool:
        return self.deployment_value < self.observed_min or self.deployment_value > self.observed_max

    @property
    def near_boundary(self) -> bool:
        if self.extrapolation:
            return True
        width = self.observed_max - self.observed_min
        margin = self.review_margin * width
        return self.deployment_value - self.observed_min <= margin or self.observed_max - self.deployment_value <= margin


@dataclass(frozen=True, slots=True)
class NoveltyAssessment:
    features: tuple[FeatureSupport, ...]
    ood_threshold: float = 0.0

    def __post_init__(self) -> None:
        if not self.features:
            raise ValueError("novelty assessment requires features")
        if self.ood_threshold < 0 or not math.isfinite(self.ood_threshold):
            raise ValueError("ood_threshold must be finite and non-negative")

    @property
    def extrapolation(self) -> bool:
        return any(item.normalized_distance > self.ood_threshold for item in self.features)

    @property
    def near_boundary(self) -> bool:
        return any(item.near_boundary for item in self.features)

    @property
    def max_distance(self) -> float:
        return max(item.normalized_distance for item in self.features)

    @property
    def state(self) -> RuntimeState:
        if self.extrapolation:
            return RuntimeState.ABSTAIN
        if self.near_boundary:
            return RuntimeState.REVIEW
        return RuntimeState.RELEASE


class CausalIdentificationStatus(StrEnum):
    DESCRIPTIVE = "descriptive"
    CONDITIONAL = "conditional"
    IDENTIFIED = "identified"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class CausalRuntimeContract:
    estimand: str
    treatment: str
    outcome: str
    assumptions: tuple[str, ...]
    causal_claim_requested: bool
    sensitivity_score: float | None = None

    def __post_init__(self) -> None:
        if not self.estimand or not self.treatment or not self.outcome:
            raise ValueError("causal estimand, treatment and outcome are required")
        if not self.assumptions:
            raise ValueError("causal assumptions are required")
        if self.sensitivity_score is not None and not 0 <= self.sensitivity_score <= 1:
            raise ValueError("sensitivity_score must be in [0,1]")

    @property
    def status(self) -> CausalIdentificationStatus:
        normalized = {item.strip().lower() for item in self.assumptions}
        required = {"consistency", "conditional_exchangeability", "positivity"}
        if required.issubset(normalized):
            return CausalIdentificationStatus.IDENTIFIED
        if self.causal_claim_requested:
            return CausalIdentificationStatus.ABSTAIN
        if normalized & {"consistency", "positivity", "exchangeability", "conditional_exchangeability"}:
            return CausalIdentificationStatus.CONDITIONAL
        return CausalIdentificationStatus.DESCRIPTIVE


@dataclass(frozen=True, slots=True)
class RobustnessGate:
    satisficing_rate: float
    worst_case: float
    max_regret: float
    minimum_satisficing_rate: float
    minimum_worst_case: float
    maximum_regret: float

    def __post_init__(self) -> None:
        values = (self.satisficing_rate, self.minimum_satisficing_rate, self.minimum_worst_case, self.maximum_regret)
        if any(not math.isfinite(v) for v in values):
            raise ValueError("robustness thresholds must be finite")
        if not 0 <= self.satisficing_rate <= 1:
            raise ValueError("satisficing_rate must be in [0,1]")
        if not math.isfinite(self.worst_case) or not math.isfinite(self.max_regret):
            raise ValueError("robustness values must be finite")

    @property
    def state(self) -> RuntimeState:
        if self.satisficing_rate < self.minimum_satisficing_rate:
            return RuntimeState.ABSTAIN
        if self.worst_case < self.minimum_worst_case or self.max_regret > self.maximum_regret:
            return RuntimeState.REVIEW
        return RuntimeState.RELEASE


@dataclass(frozen=True, slots=True)
class ScientificRuntimeAssessment:
    assessment_id: str
    decision_id: str
    evidence_ids: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    reference_class: ReferenceClassAssessment
    novelty: NoveltyAssessment
    causal: CausalRuntimeContract | None
    robustness: RobustnessGate | None
    uncertainty: float
    code_revision: str
    configuration_hash: str
    method_version: str = "scientific-runtime-v1"
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.assessment_id or not self.decision_id:
            raise ValueError("assessment and decision identity are required")
        if not self.evidence_ids or not self.provenance_refs:
            raise ValueError("scientific runtime assessment requires evidence and provenance")
        if not self.code_revision or not self.configuration_hash:
            raise ValueError("code revision and configuration hash are required")
        if not 0 <= self.uncertainty <= 1 or not math.isfinite(self.uncertainty):
            raise ValueError("uncertainty must be in [0,1]")

    @property
    def state(self) -> RuntimeState:
        states = [self.reference_class.state, self.novelty.state]
        if self.causal is not None and self.causal.causal_claim_requested:
            states.append(RuntimeState.ABSTAIN if self.causal.status is CausalIdentificationStatus.ABSTAIN else RuntimeState.REVIEW if self.causal.status is CausalIdentificationStatus.CONDITIONAL else RuntimeState.RELEASE)
        if self.robustness is not None:
            states.append(self.robustness.state)
        if RuntimeState.ABSTAIN in states:
            return RuntimeState.ABSTAIN
        if RuntimeState.REVIEW in states:
            return RuntimeState.REVIEW
        return RuntimeState.RELEASE

    @property
    def mechanism_satisfied(self) -> bool:
        return self.state is not RuntimeState.ABSTAIN

    @property
    def model_conflict(self) -> bool:
        return self.reference_class.state is not RuntimeState.RELEASE or self.novelty.state is not RuntimeState.RELEASE

    @property
    def effective_uncertainty(self) -> float:
        value = self.uncertainty
        if self.novelty.extrapolation:
            value = max(value, 0.95)
        if self.reference_class.state is RuntimeState.ABSTAIN:
            value = max(value, 0.9)
        if self.causal is not None and self.causal.status is CausalIdentificationStatus.CONDITIONAL:
            value = max(value, 0.7)
        if self.robustness is not None and self.robustness.state is RuntimeState.REVIEW:
            value = max(value, 0.6)
        return min(1.0, value)

    @property
    def findings(self) -> tuple[str, ...]:
        findings: list[str] = []
        if self.reference_class.state is not RuntimeState.RELEASE:
            findings.append("reference_class_unsupported")
        if self.novelty.extrapolation:
            findings.append("deployment_outside_observed_support")
        elif self.novelty.near_boundary:
            findings.append("deployment_near_observed_boundary")
        if self.causal is not None and self.causal.status is CausalIdentificationStatus.ABSTAIN:
            findings.append("causal_identification_unsatisfied")
        elif self.causal is not None and self.causal.status is CausalIdentificationStatus.CONDITIONAL:
            findings.append("causal_claim_conditional")
        if self.robustness is not None and self.robustness.state is not RuntimeState.RELEASE:
            findings.append("robustness_gate_not_met")
        return tuple(findings)


class ScientificRuntimeLedger:
    """Append-only persistence and integrity verification for runtime assessments."""

    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_runtime_assessments(
                assessment_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL,
                payload TEXT NOT NULL, assessment_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL, created_at TEXT NOT NULL
            )""")
            columns = {row[1] for row in db.execute("PRAGMA table_info(scientific_runtime_assessments)")}
            if "previous_hash" not in columns:
                db.execute("ALTER TABLE scientific_runtime_assessments ADD COLUMN previous_hash TEXT NOT NULL DEFAULT ''")

    def append(self, assessment: ScientificRuntimeAssessment) -> None:
        payload = _canonical(asdict(assessment))
        created_at = assessment.created_at or datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.storage_path) as db:
            if db.execute("SELECT 1 FROM scientific_runtime_assessments WHERE assessment_id=?", (assessment.assessment_id,)).fetchone():
                raise ValueError("scientific runtime assessment already exists")
            previous = db.execute("SELECT assessment_hash FROM scientific_runtime_assessments ORDER BY created_at DESC, assessment_id DESC LIMIT 1").fetchone()
            previous_hash = previous[0] if previous else ""
            digest = _digest({"payload": payload, "previous_hash": previous_hash})
            db.execute("INSERT INTO scientific_runtime_assessments (assessment_id,decision_id,payload,assessment_hash,previous_hash,created_at) VALUES(?,?,?,?,?,?)", (assessment.assessment_id, assessment.decision_id, payload, digest, previous_hash, created_at))

    def verify_integrity(self) -> bool:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT assessment_id,payload,assessment_hash,previous_hash FROM scientific_runtime_assessments ORDER BY created_at,assessment_id").fetchall()
        previous = ""
        for assessment_id, payload, record_hash, previous_hash in rows:
            if not assessment_id or previous_hash != previous or record_hash != _digest({"payload": payload, "previous_hash": previous_hash}):
                return False
            previous = record_hash
        return True


__all__ = ["CausalIdentificationStatus", "CausalRuntimeContract", "FeatureSupport", "NoveltyAssessment", "ReferenceClassAssessment", "RobustnessGate", "RuntimeState", "ScientificRuntimeAssessment", "ScientificRuntimeLedger"]
