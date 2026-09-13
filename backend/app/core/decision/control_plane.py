"""Decision-system control plane for CeutIA."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
from math import isfinite
from typing import Mapping, Protocol, Sequence


class EpistemicKind(StrEnum):
    OBSERVATION = "observation"
    SIGNAL = "signal"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    PREDICTION = "prediction"
    SCENARIO = "scenario"
    DECISION = "decision"


class EvidenceDisposition(StrEnum):
    ACCEPT = "accept"
    DOWNWEIGHT = "downweight"
    QUARANTINE = "quarantine"
    REQUIRE_CORROBORATION = "require_corroboration"
    BLOCK = "block"


class DecisionDisposition(StrEnum):
    RECOMMEND = "recommend"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"
    BLOCK = "block"
    ACQUIRE_INFORMATION = "acquire_information"


@dataclass(frozen=True, slots=True)
class EvidenceAssessment:
    evidence_id: str
    source_id: str
    base_weight: float
    adversarial_risk: float = 0.0
    contradiction_weight: float = 0.0
    independent_origin: bool = True
    disposition: EvidenceDisposition = EvidenceDisposition.ACCEPT

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.source_id:
            raise ValueError("evidence requires identity and source")
        if not 0.0 <= self.base_weight <= 1.0:
            raise ValueError("base_weight must be in [0,1]")
        if not 0.0 <= self.adversarial_risk <= 1.0:
            raise ValueError("adversarial_risk must be in [0,1]")
        if not 0.0 <= self.contradiction_weight <= 1.0:
            raise ValueError("contradiction_weight must be in [0,1]")

    def effective_weight(self) -> float:
        if self.disposition in {EvidenceDisposition.BLOCK, EvidenceDisposition.QUARANTINE}:
            return 0.0
        multiplier = 0.5 if self.disposition is EvidenceDisposition.DOWNWEIGHT else 1.0
        multiplier *= 0.5 if self.disposition is EvidenceDisposition.REQUIRE_CORROBORATION else 1.0
        multiplier *= max(0.0, 1.0 - self.adversarial_risk)
        multiplier *= max(0.0, 1.0 - self.contradiction_weight)
        return self.base_weight * multiplier


@dataclass(frozen=True, slots=True)
class ConflictResolution:
    claim_id: str
    supporting_ids: tuple[str, ...]
    contradicting_ids: tuple[str, ...]
    independent_support_weight: float
    independent_contradiction_weight: float
    unresolved: bool

    @property
    def net_support(self) -> float:
        return self.independent_support_weight - self.independent_contradiction_weight


class EvidenceConflictResolver:
    def resolve(self, claim_id: str, supporting: Sequence[EvidenceAssessment], contradicting: Sequence[EvidenceAssessment]) -> ConflictResolution:
        support = tuple(x for x in supporting if x.independent_origin)
        contradiction = tuple(x for x in contradicting if x.independent_origin)
        sw = sum(x.effective_weight() for x in support)
        cw = sum(x.effective_weight() for x in contradiction)
        unresolved = bool(support and contradiction and abs(sw - cw) <= max(0.25, 0.25 * max(sw, cw)))
        return ConflictResolution(claim_id, tuple(x.evidence_id for x in supporting), tuple(x.evidence_id for x in contradicting), sw, cw, unresolved)


@dataclass(frozen=True, slots=True)
class UncertaintyState:
    value: float
    lower: float | None = None
    upper: float | None = None
    source_refs: tuple[str, ...] = ()
    method: str = "declared"

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("uncertainty must be in [0,1]")
        if self.lower is not None and not 0.0 <= self.lower <= 1.0:
            raise ValueError("lower uncertainty bound must be in [0,1]")
        if self.upper is not None and not 0.0 <= self.upper <= 1.0:
            raise ValueError("upper uncertainty bound must be in [0,1]")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("lower uncertainty bound cannot exceed upper bound")

    def propagate(self, *children: "UncertaintyState", method: str = "conservative") -> "UncertaintyState":
        values = (self, *children)
        value = max(x.value for x in values) if method == "conservative" else sum(x.value for x in values) / len(values)
        return UncertaintyState(value, source_refs=tuple(r for x in values for r in x.source_refs), method=method)


@dataclass(frozen=True, slots=True)
class EpistemicRecord:
    object_id: str
    kind: EpistemicKind
    input_refs: tuple[str, ...]
    as_of: str
    valid_from: str | None
    valid_until: str | None
    uncertainty: UncertaintyState
    provenance_refs: tuple[str, ...]
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScenarioSpec:
    scenario_id: str
    probability: float
    assumptions: tuple[str, ...]
    state_refs: tuple[str, ...]
    consequence: Mapping[str, float]
    uncertainty: UncertaintyState

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("scenario probability must be in [0,1]")
        if any(not isfinite(float(v)) for v in self.consequence.values()):
            raise ValueError("scenario consequences must be finite")


class ScenarioGenerator:
    def generate(self, branches: Sequence[ScenarioSpec]) -> tuple[ScenarioSpec, ...]:
        if not branches:
            raise ValueError("at least one scenario is required")
        total = sum(x.probability for x in branches)
        if abs(total - 1.0) > 1e-9:
            raise ValueError("scenario probabilities must sum to one")
        return tuple(branches)


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    human_review_required: bool
    reason: str
    policy_version: str


class DecisionPolicy(Protocol):
    def evaluate(self, *, purpose: str, uncertainty: float, restricted: bool) -> PolicyDecision: ...


@dataclass(frozen=True, slots=True)
class DefaultDecisionPolicy:
    version: str = "1.0"

    def evaluate(self, *, purpose: str, uncertainty: float, restricted: bool) -> PolicyDecision:
        if not purpose.strip():
            return PolicyDecision(False, False, "decision purpose is required", self.version)
        if restricted:
            return PolicyDecision(False, False, "restricted information requires an authorized policy path", self.version)
        if not 0.0 <= uncertainty <= 1.0:
            return PolicyDecision(False, False, "uncertainty is invalid", self.version)
        if uncertainty >= 1.0:
            return PolicyDecision(False, False, "decision uncertainty is indeterminate", self.version)
        return PolicyDecision(True, False, "structural controls passed; risk policy determines review disposition", self.version)


@dataclass(frozen=True, slots=True)
class DecisionManifest:
    decision_id: str
    state_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    model_refs: tuple[str, ...]
    hypothesis_refs: tuple[str, ...]
    transformation_refs: tuple[str, ...]
    assumption_refs: tuple[str, ...]
    scenario_refs: tuple[str, ...]
    utility_definition_ref: str
    constraint_refs: tuple[str, ...]
    policy_version: str
    configuration_hash: str
    code_revision: str
    created_at: str

    def complete(self) -> bool:
        return bool(self.decision_id and self.state_refs and self.evidence_refs and self.model_refs and self.scenario_refs and self.utility_definition_ref and self.policy_version and self.configuration_hash and self.code_revision)

    def fingerprint(self) -> str:
        payload = {"decision_id": self.decision_id, "state_refs": self.state_refs, "evidence_refs": self.evidence_refs, "model_refs": self.model_refs, "hypothesis_refs": self.hypothesis_refs, "transformation_refs": self.transformation_refs, "assumption_refs": self.assumption_refs, "scenario_refs": self.scenario_refs, "utility_definition_ref": self.utility_definition_ref, "constraint_refs": self.constraint_refs, "policy_version": self.policy_version, "configuration_hash": self.configuration_hash, "code_revision": self.code_revision}
        return sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class DecisionAuditEvent:
    event_id: str
    decision_id: str
    event_type: str
    payload: Mapping[str, object]
    previous_hash: str
    event_hash: str
    timestamp: str


class AuditStore(Protocol):
    def append(self, event: DecisionAuditEvent) -> None: ...
    def events(self, decision_id: str) -> tuple[DecisionAuditEvent, ...]: ...


class InMemoryAuditStore:
    def __init__(self) -> None:
        self._events: list[DecisionAuditEvent] = []

    def append(self, event: DecisionAuditEvent) -> None:
        self._events.append(event)

    def events(self, decision_id: str) -> tuple[DecisionAuditEvent, ...]:
        return tuple(x for x in self._events if x.decision_id == decision_id)


class DecisionAuditChain:
    def __init__(self, store: AuditStore | None = None) -> None:
        self.store = store or InMemoryAuditStore()

    def append(self, decision_id: str, event_type: str, payload: Mapping[str, object]) -> DecisionAuditEvent:
        prior = self.store.events(decision_id)
        previous_hash = prior[-1].event_hash if prior else "GENESIS"
        timestamp = datetime.now(timezone.utc).isoformat()
        event_id = sha256(f"{decision_id}:{event_type}:{timestamp}".encode()).hexdigest()
        canonical = json.dumps(dict(payload), sort_keys=True, default=str, separators=(",", ":"))
        event_hash = sha256(f"{previous_hash}|{event_id}|{canonical}".encode()).hexdigest()
        event = DecisionAuditEvent(event_id, decision_id, event_type, dict(payload), previous_hash, event_hash, timestamp)
        self.store.append(event)
        return event


@dataclass(frozen=True, slots=True)
class HumanDecisionReview:
    decision_id: str
    review_id: str
    actor_id: str
    authority: str
    original_disposition: str
    human_disposition: str
    reason: str
    modified_option: str | None
    timestamp: str


@dataclass(frozen=True, slots=True)
class DecisionOutcome:
    decision_id: str
    option_id: str
    expected_utility: float
    observed_utility: float
    expected_harm: float
    observed_harm: float
    outcome_at: str

    @property
    def utility_error(self) -> float:
        return self.observed_utility - self.expected_utility

    @property
    def harm_error(self) -> float:
        return self.observed_harm - self.expected_harm


@dataclass(frozen=True, slots=True)
class DecisionQuality:
    decision_id: str
    utility_error: float
    harm_error: float
    realized_utility: float
    realized_harm: float
    regret: float | None
    quality_score: float


class DecisionQualityEvaluator:
    def evaluate(self, outcome: DecisionOutcome, *, best_alternative_utility: float | None = None) -> DecisionQuality:
        regret = None if best_alternative_utility is None else max(0.0, best_alternative_utility - outcome.observed_utility)
        score = outcome.observed_utility - outcome.observed_harm
        return DecisionQuality(outcome.decision_id, outcome.utility_error, outcome.harm_error, outcome.observed_utility, outcome.observed_harm, regret, score)


@dataclass(frozen=True, slots=True)
class DecisionControlResult:
    disposition: DecisionDisposition
    reason: str
    uncertainty: UncertaintyState
    manifest: DecisionManifest
    audit_event_id: str


class DecisionControlPlane:
    def __init__(self, *, policy: DecisionPolicy | None = None, audit: DecisionAuditChain | None = None) -> None:
        self.policy = policy or DefaultDecisionPolicy()
        self.audit = audit or DecisionAuditChain()

    def authorize(self, *, decision_id: str, purpose: str, uncertainty: UncertaintyState, restricted: bool, manifest: DecisionManifest, evidence_assessments: Sequence[EvidenceAssessment] = (), conflict_resolutions: Sequence[ConflictResolution] = ()) -> DecisionControlResult:
        complete = manifest.complete()
        evidence_ids = set(manifest.evidence_refs)
        assessed_ids = {item.evidence_id for item in evidence_assessments}
        missing_assessments = tuple(sorted(evidence_ids - assessed_ids))
        blocked = tuple(item.evidence_id for item in evidence_assessments if item.disposition in {EvidenceDisposition.BLOCK, EvidenceDisposition.QUARANTINE})
        corroboration = tuple(item.evidence_id for item in evidence_assessments if item.disposition is EvidenceDisposition.REQUIRE_CORROBORATION)
        high_adversarial = tuple(item.evidence_id for item in evidence_assessments if item.adversarial_risk >= 0.75)
        unresolved_conflicts = tuple(item.claim_id for item in conflict_resolutions if item.unresolved)
        if not complete:
            reason = "decision manifest is incomplete; decision execution is blocked"
            event = self.audit.append(decision_id, "decision_control", {"disposition": DecisionDisposition.ABSTAIN.value, "reason": reason, "uncertainty": uncertainty.value, "manifest_complete": False, "manifest_fingerprint": manifest.fingerprint()})
            return DecisionControlResult(DecisionDisposition.ABSTAIN, reason, uncertainty, manifest, event.event_id)
        if missing_assessments:
            disposition = DecisionDisposition.ABSTAIN
            reason = "declared decision evidence is not fully assessed"
        elif blocked:
            disposition = DecisionDisposition.ABSTAIN
            reason = "decision evidence contains blocked or quarantined items"
        elif unresolved_conflicts or corroboration or high_adversarial:
            disposition = DecisionDisposition.HUMAN_REVIEW
            reason = "evidence requires unresolved-conflict, corroboration or adversarial review"
        else:
            policy = self.policy.evaluate(purpose=purpose, uncertainty=uncertainty.value, restricted=restricted)
            if not policy.allowed:
                disposition = DecisionDisposition.ABSTAIN
            elif policy.human_review_required:
                disposition = DecisionDisposition.HUMAN_REVIEW
            else:
                disposition = DecisionDisposition.RECOMMEND
            reason = policy.reason
        event = self.audit.append(decision_id, "decision_control", {"disposition": disposition.value, "reason": reason, "uncertainty": uncertainty.value, "manifest_complete": True, "manifest_fingerprint": manifest.fingerprint(), "policy_version": manifest.policy_version, "state_refs": manifest.state_refs, "evidence_refs": manifest.evidence_refs, "assessed_evidence_refs": tuple(sorted(assessed_ids)), "missing_evidence_assessments": missing_assessments, "blocked_evidence": blocked, "corroboration_required": corroboration, "high_adversarial_evidence": high_adversarial, "unresolved_conflicts": unresolved_conflicts, "model_refs": manifest.model_refs, "hypothesis_refs": manifest.hypothesis_refs, "transformation_refs": manifest.transformation_refs, "assumption_refs": manifest.assumption_refs, "scenario_refs": manifest.scenario_refs, "constraint_refs": manifest.constraint_refs, "configuration_hash": manifest.configuration_hash, "code_revision": manifest.code_revision})
        return DecisionControlResult(disposition, reason, uncertainty, manifest, event.event_id)


__all__ = ["AuditStore", "ConflictResolution", "DecisionAuditChain", "DecisionAuditEvent", "DecisionControlPlane", "DecisionControlResult", "DecisionDisposition", "DecisionManifest", "DecisionOutcome", "DecisionPolicy", "DecisionQuality", "DecisionQualityEvaluator", "DefaultDecisionPolicy", "EpistemicKind", "EpistemicRecord", "EvidenceAssessment", "EvidenceConflictResolver", "EvidenceDisposition", "HumanDecisionReview", "InMemoryAuditStore", "PolicyDecision", "ScenarioGenerator", "ScenarioSpec", "UncertaintyState"]
