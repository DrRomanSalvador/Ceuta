"""Integrated decision lifecycle for CeutIA.

This module composes existing sensing, evidence, decision, governance and
persistence primitives. It does not replace the existing decision engines.
It provides the missing orchestration boundary that makes their contracts
participate in one auditable lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Callable, Mapping, Sequence

from app.core.decision.control_plane import (
    ConflictResolution,
    DecisionAuditChain,
    DecisionControlPlane,
    DecisionDisposition,
    DecisionManifest,
    EvidenceAssessment,
    EvidenceConflictResolver,
    EvidenceDisposition,
    UncertaintyState,
)
from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.decision_system import (
    DecisionContext,
    DecisionMode,
    DecisionOption,
    DecisionRecommendation,
    DecisionSystem,
)
from app.core.decision.information_boundary import InformationBoundary, InformationVisibility
from app.core.decision.lineage import DecisionLineage, LineageNode
from app.core.decision.review_policy import DecisionRisk, ReviewDisposition, ReviewPolicy
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.runtime.model_governance import ModelGovernance, ModelGovernanceRecord


@dataclass(frozen=True, slots=True)
class BitemporalRef:
    """A versioned fact with valid-time and system/knowledge-time semantics."""

    valid_from: datetime
    valid_until: datetime | None
    recorded_from: datetime
    recorded_until: datetime | None
    version_id: str

    def __post_init__(self) -> None:
        values = (self.valid_from, self.recorded_from)
        if any(value.tzinfo is None or value.utcoffset() is None for value in values):
            raise ValueError("bitemporal timestamps must be timezone-aware")
        for value in (self.valid_until, self.recorded_until):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("bitemporal timestamps must be timezone-aware")
        if self.valid_until is not None and self.valid_until <= self.valid_from:
            raise ValueError("valid interval must be ordered")
        if self.recorded_until is not None and self.recorded_until <= self.recorded_from:
            raise ValueError("recorded interval must be ordered")
        if not self.version_id.strip():
            raise ValueError("version_id is required")

    def valid_at(self, at: datetime) -> bool:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("point-in-time query requires timezone-aware timestamp")
        at = at.astimezone(timezone.utc)
        start = self.valid_from.astimezone(timezone.utc)
        end = self.valid_until.astimezone(timezone.utc) if self.valid_until else None
        return start <= at and (end is None or at < end)

    def known_at(self, at: datetime) -> bool:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("point-in-time query requires timezone-aware timestamp")
        at = at.astimezone(timezone.utc)
        start = self.recorded_from.astimezone(timezone.utc)
        end = self.recorded_until.astimezone(timezone.utc) if self.recorded_until else None
        return start <= at and (end is None or at < end)


@dataclass(frozen=True, slots=True)
class DecisionEvidence:
    evidence_id: str
    source_id: str
    claim_id: str
    content_hash: str
    provenance_refs: tuple[str, ...]
    temporal: BitemporalRef
    assessment: EvidenceAssessment
    visibility: InformationVisibility = InformationVisibility.PUBLIC

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.source_id or not self.claim_id:
            raise ValueError("decision evidence requires evidence, source and claim identity")
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 digest")
        if not self.provenance_refs:
            raise ValueError("decision evidence requires provenance references")
        if self.assessment.evidence_id != self.evidence_id:
            raise ValueError("evidence assessment identity mismatch")
        if self.assessment.source_id != self.source_id:
            raise ValueError("evidence assessment source mismatch")


@dataclass(frozen=True, slots=True)
class DecisionSignal:
    signal_id: str
    evidence_refs: tuple[str, ...]
    state_ref: str
    uncertainty: UncertaintyState
    detected_at: datetime


@dataclass(frozen=True, slots=True)
class DecisionInference:
    inference_id: str
    signal_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    method: str
    assumptions: tuple[str, ...]
    uncertainty: UncertaintyState
    causal: bool = False


@dataclass(frozen=True, slots=True)
class DecisionHypothesis:
    hypothesis_id: str
    inference_refs: tuple[str, ...]
    supporting_refs: tuple[str, ...]
    contradicting_refs: tuple[str, ...]
    status: str
    uncertainty: UncertaintyState


@dataclass(frozen=True, slots=True)
class DecisionPrediction:
    prediction_id: str
    hypothesis_refs: tuple[str, ...]
    model_ref: str
    target: str
    horizon: str
    probability: float | None
    uncertainty: UncertaintyState
    assumptions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionLifecycleResult:
    decision_id: str
    disposition: DecisionDisposition
    recommendation: DecisionRecommendation
    control_reason: str
    audit_event_id: str
    lineage: DecisionLineage
    uncertainty: UncertaintyState
    degraded_reasons: tuple[str, ...]


class DecisionLifecycleEngine:
    """Single orchestration boundary for evidence-to-decision execution."""

    def __init__(
        self,
        store: SQLiteDecisionStore,
        *,
        code_revision: str,
        configuration: ConfigurationProvenance,
        review_policy: ReviewPolicy | None = None,
        decision_system: DecisionSystem | None = None,
        model_governance: ModelGovernance | None = None,
    ) -> None:
        if not code_revision.strip() or code_revision.lower() in {"unknown", "dirty", "unresolved"}:
            raise ValueError("exact reproducible code_revision is required")
        self.store = store
        self.audit = DecisionAuditChain(store)
        self.control = DecisionControlPlane(
            policy=_LifecyclePolicy(review_policy or self._default_policy(), configuration.version),
            audit=self.audit,
        )
        self.decisions = decision_system or DecisionSystem(review_policy=review_policy or self._default_policy())
        self.model_governance = model_governance or ModelGovernance()
        self.code_revision = code_revision
        self.configuration = configuration
        self.conflicts = EvidenceConflictResolver()

    @staticmethod
    def _default_policy() -> ReviewPolicy:
        return ReviewPolicy(
            policy_version="decision-risk-v1",
            auto_allowed=frozenset({DecisionRisk.LOW}),
            review_required=frozenset({DecisionRisk.MODERATE, DecisionRisk.HIGH}),
            abstain_required=frozenset({DecisionRisk.CRITICAL}),
        )

    def _manifest(
        self,
        context: DecisionContext,
        evidence: Sequence[DecisionEvidence],
        state_refs: Sequence[str],
        hypothesis_refs: Sequence[str],
        model_refs: Sequence[str],
        scenario_refs: Sequence[str],
        assumption_refs: Sequence[str],
        transformation_refs: Sequence[str],
        constraint_refs: Sequence[str],
    ) -> DecisionManifest:
        return DecisionManifest(
            decision_id=context.decision_id,
            state_refs=tuple(state_refs),
            evidence_refs=tuple(item.evidence_id for item in evidence),
            model_refs=tuple(model_refs),
            hypothesis_refs=tuple(hypothesis_refs),
            transformation_refs=tuple(transformation_refs),
            assumption_refs=tuple(assumption_refs),
            scenario_refs=tuple(scenario_refs),
            utility_definition_ref="decision-utility:v1",
            constraint_refs=tuple(constraint_refs),
            policy_version=self.control.policy.version if isinstance(self.control.policy, _LifecyclePolicy) else "unresolved",
            configuration_hash=self.configuration.fingerprint(),
            code_revision=self.code_revision,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _degraded_reasons(
        evidence: Sequence[DecisionEvidence],
        *,
        state_available: bool,
        models_available: bool,
        persistence_available: bool,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if not evidence:
            reasons.append("no decision evidence")
        if any(item.assessment.disposition in {EvidenceDisposition.BLOCK, EvidenceDisposition.QUARANTINE} for item in evidence):
            reasons.append("blocked or quarantined evidence present")
        if not state_available:
            reasons.append("state unavailable")
        if not models_available:
            reasons.append("required model release unavailable")
        if not persistence_available:
            reasons.append("durable persistence unavailable")
        return tuple(reasons)

    def execute(
        self,
        context: DecisionContext,
        options: Sequence[DecisionOption],
        evidence: Sequence[DecisionEvidence],
        *,
        state_refs: Sequence[str],
        signal_refs: Sequence[str] = (),
        inference_refs: Sequence[str] = (),
        hypothesis_refs: Sequence[str] = (),
        model_refs: Sequence[str] = (),
        scenario_refs: Sequence[str] = (),
        assumption_refs: Sequence[str] = (),
        transformation_refs: Sequence[str] = (),
        constraint_refs: Sequence[str] = (),
        conflict_resolutions: Sequence[ConflictResolution] = (),
        purpose: str,
        restricted: bool = False,
        boundaries: Sequence[InformationBoundary] = (),
        output_visibility: InformationVisibility = InformationVisibility.PUBLIC,
        mode: DecisionMode = DecisionMode.ROBUST,
        at: datetime | None = None,
        state_available: bool = True,
        model_releases: Mapping[str, ModelGovernanceRecord] | None = None,
    ) -> DecisionLifecycleResult:
        timestamp = at or datetime.now(timezone.utc)
        for boundary in boundaries:
            boundary.assert_emit(output_visibility)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("decision timestamp must be timezone-aware")
        if not state_refs:
            raise ValueError("decision requires state references")
        if not options:
            raise ValueError("decision requires admissible options")

        assessments = tuple(item.assessment for item in evidence)
        evidence_ids = {item.evidence_id for item in evidence}
        missing = tuple(sorted(set(context.assumptions) & evidence_ids))
        del missing
        model_releases = model_releases or {}
        model_reasons: list[str] = []
        for model_ref in model_refs:
            release = model_releases.get(model_ref)
            if release is None or not release.calibrated or not self.model_governance.validate(release, timestamp):
                model_reasons.append(f"model release unavailable, uncalibrated or outside validity: {model_ref}")

        conflicts = tuple(conflict_resolutions)
        manifest = self._manifest(
            context,
            evidence,
            state_refs,
            hypothesis_refs,
            model_refs,
            scenario_refs,
            assumption_refs,
            transformation_refs,
            constraint_refs,
        )
        uncertainty = UncertaintyState(
            max((item.assessment.adversarial_risk for item in evidence), default=1.0 if not evidence else 0.0),
            source_refs=tuple(item.evidence_id for item in evidence),
            method="evidence-adversarial-risk-conservative-max",
        )
        degraded = self._degraded_reasons(
            evidence,
            state_available=state_available,
            models_available=not model_reasons,
            persistence_available=True,
        )
        if model_reasons:
            degraded = (*degraded, *model_reasons)

        if not evidence or not state_available or model_reasons:
            control = self.control.authorize(
                decision_id=context.decision_id,
                purpose=purpose,
                uncertainty=UncertaintyState(1.0, source_refs=tuple(item.evidence_id for item in evidence), method="degraded-mode"),
                restricted=restricted,
                manifest=manifest,
                evidence_assessments=assessments,
                conflict_resolutions=conflicts,
            )
            recommendation = self.decisions._abstain(context, mode, "; ".join(degraded), (f"audit:{control.audit_event_id}",), ("reevaluate after recovery",))
        else:
            control = self.control.authorize(
                decision_id=context.decision_id,
                purpose=purpose,
                uncertainty=uncertainty,
                restricted=restricted,
                manifest=manifest,
                evidence_assessments=assessments,
                conflict_resolutions=conflicts,
            )
            provenance = tuple(
                [f"evidence:{item.evidence_id}" for item in evidence]
                + [f"signal:{ref}" for ref in signal_refs]
                + [f"inference:{ref}" for ref in inference_refs]
                + [f"hypothesis:{ref}" for ref in hypothesis_refs]
                + [f"model:{ref}" for ref in model_refs]
                + [f"audit:{control.audit_event_id}"]
            )
            if control.disposition in {DecisionDisposition.ABSTAIN, DecisionDisposition.BLOCK}:
                recommendation = self.decisions._abstain(context, mode, control.reason, provenance, ("reevaluate after new evidence",))
            elif control.disposition is DecisionDisposition.HUMAN_REVIEW:
                recommendation = self.decisions._abstain(context, mode, "human review required before execution", provenance, ("reevaluate after human disposition",))
            else:
                recommendation = self.decisions.recommend(context, options, mode=mode, provenance=provenance, reevaluation_triggers=("reevaluate after new evidence", "material state change", "model validity change"), at=timestamp)

        terminal = recommendation.disposition.value
        nodes = (
            LineageNode(f"{context.decision_id}:evidence", "evidence", evidence_refs=tuple(item.evidence_id for item in evidence), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:state", "state", input_refs=tuple(item.evidence_id for item in evidence), output_refs=tuple(state_refs), evidence_refs=tuple(item.evidence_id for item in evidence), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:analysis", "analysis", input_refs=tuple(state_refs), output_refs=tuple(signal_refs) + tuple(inference_refs) + tuple(hypothesis_refs), evidence_refs=tuple(item.evidence_id for item in evidence), model_refs=tuple(model_refs), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:decision", "decision", input_refs=tuple(scenario_refs) + tuple(hypothesis_refs), output_refs=(context.decision_id, recommendation.option_id), evidence_refs=tuple(item.evidence_id for item in evidence), model_refs=tuple(model_refs), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
        )
        lineage = DecisionLineage(context.decision_id, nodes, terminal, manifest.fingerprint())
        self.store.record_lineage(lineage)
        self.store.record_cycle(system_id="ceutia", as_of=manifest.created_at, decision_id=context.decision_id, option_id=recommendation.option_id, disposition=terminal, lineage=tuple(node.node_id for node in nodes), stages=tuple({"stage": node.stage, "inputs": node.input_refs, "outputs": node.output_refs} for node in nodes))
        return DecisionLifecycleResult(context.decision_id, recommendation.disposition, recommendation, control.reason, control.audit_event_id, lineage, uncertainty, tuple(degraded))


@dataclass(frozen=True, slots=True)
class _LifecyclePolicy:
    base: ReviewPolicy
    version: str

    def evaluate(self, *, purpose: str, uncertainty: float, restricted: bool):
        if restricted:
            from app.core.decision.control_plane import PolicyDecision
            return PolicyDecision(False, False, "restricted information requires an authorized policy path", self.version)
        disposition = self.base.disposition(DecisionRisk.CRITICAL if uncertainty >= 1.0 else DecisionRisk.HIGH if uncertainty >= 0.75 else DecisionRisk.MODERATE if uncertainty >= 0.5 else DecisionRisk.LOW)
        from app.core.decision.control_plane import PolicyDecision
        return PolicyDecision(disposition is ReviewDisposition.AUTO, disposition is ReviewDisposition.HUMAN_REVIEW, f"risk policy {self.version}: {disposition.value}", self.version)


__all__ = [
    "BitemporalRef",
    "DecisionEvidence",
    "DecisionSignal",
    "DecisionInference",
    "DecisionHypothesis",
    "DecisionPrediction",
    "DecisionLifecycleEngine",
    "DecisionLifecycleResult",
]
