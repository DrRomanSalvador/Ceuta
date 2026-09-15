"""Integrated decision lifecycle for CeutIA.

This module composes existing sensing, evidence, decision, governance and
persistence primitives. It also makes cross-cutting scientific constraints
and intervention-aware validation part of the canonical runtime contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Sequence

from app.core.decision.control_plane import (
    ConflictResolution, DecisionAuditChain, DecisionControlPlane, DecisionDisposition,
    DecisionManifest, EvidenceAssessment, EvidenceConflictResolver, EvidenceDisposition,
    UncertaintyState,
)
from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.decision_system import (
    DecisionContext, DecisionMode, DecisionOption, DecisionRecommendation, DecisionSystem,
)
from app.core.decision.information_boundary import InformationBoundary, InformationVisibility
from app.core.decision.lineage import DecisionLineage, LineageNode
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.decision.review_policy import DecisionRisk, ReviewDisposition, ReviewPolicy
from app.core.runtime.model_governance import ModelGovernance, ModelGovernanceRecord
from app.core.scientific.governance_signals import (
    GovernanceDisposition, GovernanceInput, GovernanceSignal, ScientificGovernance,
)
from app.core.scientific.nonstationarity import NonStationarityAssessment
from app.core.scientific.scientific_runtime_contract import ScientificRuntimeAssessment, ScientificRuntimeLedger
from app.core.scientific.intervention_independent_validation import InterventionIndependentValidationLedger, ValidationObservation


@dataclass(frozen=True, slots=True)
class BitemporalRef:
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
    governance_signal: GovernanceSignal | None = None


class DecisionLifecycleEngine:
    """Single orchestration boundary for evidence-to-decision execution."""

    def __init__(self, store: SQLiteDecisionStore, *, code_revision: str, configuration: ConfigurationProvenance, review_policy: ReviewPolicy | None = None, decision_system: DecisionSystem | None = None, model_governance: ModelGovernance | None = None, scientific_governance: ScientificGovernance | None = None) -> None:
        if not code_revision.strip() or code_revision.lower() in {"unknown", "dirty", "unresolved"}:
            raise ValueError("exact reproducible code_revision is required")
        self.store = store
        self.audit = DecisionAuditChain(store)
        self.control = DecisionControlPlane(policy=_LifecyclePolicy(review_policy or self._default_policy(), configuration.version), audit=self.audit)
        self.decisions = decision_system or DecisionSystem(review_policy=review_policy or self._default_policy())
        self.model_governance = model_governance or ModelGovernance()
        self.scientific_governance = scientific_governance or ScientificGovernance(storage_path=store.path)
        self.scientific_runtime_ledger = ScientificRuntimeLedger(store.path)
        self.intervention_validation_ledger = InterventionIndependentValidationLedger(store.path)
        self.code_revision = code_revision
        self.configuration = configuration
        self.conflicts = EvidenceConflictResolver()

    @staticmethod
    def _default_policy() -> ReviewPolicy:
        return ReviewPolicy(policy_version="decision-risk-v1", auto_allowed=frozenset({DecisionRisk.LOW}), review_required=frozenset({DecisionRisk.MODERATE, DecisionRisk.HIGH}), abstain_required=frozenset({DecisionRisk.CRITICAL}))

    def _manifest(self, context: DecisionContext, evidence: Sequence[DecisionEvidence], state_refs: Sequence[str], hypothesis_refs: Sequence[str], model_refs: Sequence[str], scenario_refs: Sequence[str], assumption_refs: Sequence[str], transformation_refs: Sequence[str], constraint_refs: Sequence[str]) -> DecisionManifest:
        return DecisionManifest(decision_id=context.decision_id, state_refs=tuple(state_refs), evidence_refs=tuple(item.evidence_id for item in evidence), model_refs=tuple(model_refs), hypothesis_refs=tuple(hypothesis_refs), transformation_refs=tuple(transformation_refs), assumption_refs=tuple(assumption_refs), scenario_refs=tuple(scenario_refs), utility_definition_ref="decision-utility:v1", constraint_refs=tuple(constraint_refs), policy_version=self.control.policy.version if isinstance(self.control.policy, _LifecyclePolicy) else "unresolved", configuration_hash=self.configuration.fingerprint(), code_revision=self.code_revision, created_at=datetime.now(timezone.utc).isoformat())

    @staticmethod
    def _degraded_reasons(evidence: Sequence[DecisionEvidence], *, state_available: bool, models_available: bool, persistence_available: bool) -> tuple[str, ...]:
        reasons: list[str] = []
        if not evidence: reasons.append("no decision evidence")
        if any(item.assessment.disposition in {EvidenceDisposition.BLOCK, EvidenceDisposition.QUARANTINE} for item in evidence): reasons.append("blocked or quarantined evidence present")
        if not state_available: reasons.append("state unavailable")
        if not models_available: reasons.append("required model release unavailable")
        if not persistence_available: reasons.append("durable persistence unavailable")
        return tuple(reasons)

    def _governance_input(self, evidence: Sequence[DecisionEvidence], conflicts: Sequence[ConflictResolution], *, uncertainty: float, model_conflict: bool, mechanism_input: GovernanceInput | None, response_closure_complete: bool, decision_id: str, nonstationarity: NonStationarityAssessment | None = None, scientific_runtime_assessment: ScientificRuntimeAssessment | None = None, validation_observation: ValidationObservation | None = None) -> GovernanceInput:
        if mechanism_input is not None:
            base = mechanism_input
        else:
            if not evidence:
                raise ValueError("scientific governance requires evidence")
            weights = [item.assessment.effective_weight() for item in evidence]
            quality = sum(weights) / len(weights)
            independent = sum(1 for item in evidence if item.assessment.independent_origin) / len(evidence)
            contradiction = max((min(1.0, c.independent_contradiction_weight / max(c.independent_support_weight + c.independent_contradiction_weight, 1e-15)) for c in conflicts), default=0.0)
            provenance_refs = tuple(ref for item in evidence for ref in item.provenance_refs)
            provenance_valid = bool(provenance_refs) and all(len(item.content_hash) == 64 for item in evidence)
            base = GovernanceInput(evidence_ids=tuple(item.evidence_id for item in evidence), provenance_refs=provenance_refs, evidence_quality=quality, independent_evidence_ratio=independent, contradiction_ratio=contradiction, mechanism_satisfied=True, provenance_valid=provenance_valid, mechanism_integrity_valid=True, model_conflict=model_conflict, uncertainty=uncertainty, response_closure_complete=response_closure_complete, code_revision=self.code_revision, configuration_hash=self.configuration.fingerprint(), mechanism_ref="runtime:evidence-governance")
        provenance_refs = list(base.provenance_refs)
        findings = list(base.scientific_findings)
        mechanism_satisfied = base.mechanism_satisfied
        merged_uncertainty = base.uncertainty
        merged_model_conflict = base.model_conflict
        mechanism_refs = [base.mechanism_ref]
        if nonstationarity is not None:
            provenance_refs.append(f"nonstationarity:{nonstationarity.evidence_fingerprint}")
            mechanism_satisfied = mechanism_satisfied and nonstationarity.state != "abstain"
            merged_model_conflict = merged_model_conflict or nonstationarity.regime_change
            merged_uncertainty = max(merged_uncertainty, nonstationarity.uncertainty, 0.95 if nonstationarity.extrapolation else 0.0)
            mechanism_refs.append("nonstationarity-v1")
            if nonstationarity.extrapolation:
                findings.append("deployment_outside_observed_support")
            elif nonstationarity.regime_change:
                findings.append("regime_change_detected")
        if validation_observation is not None:
            self.intervention_validation_ledger.append(validation_observation)
            provenance_refs.append(f"intervention-validation:{validation_observation.observation_id}")
            if validation_observation.evaluation_status.value == "counterfactual_required":
                findings.append("intervention_counterfactual_required")
        if scientific_runtime_assessment is not None:
            if scientific_runtime_assessment.decision_id != decision_id:
                raise ValueError("scientific runtime assessment decision identity mismatch")
            self.scientific_runtime_ledger.append(scientific_runtime_assessment)
            provenance_refs.append(f"scientific-runtime:{scientific_runtime_assessment.assessment_id}")
            provenance_refs.append(f"scientific-runtime-method:{scientific_runtime_assessment.method_version}")
            findings.extend(scientific_runtime_assessment.findings)
            mechanism_satisfied = mechanism_satisfied and scientific_runtime_assessment.mechanism_satisfied
            merged_model_conflict = merged_model_conflict or scientific_runtime_assessment.model_conflict
            merged_uncertainty = max(merged_uncertainty, scientific_runtime_assessment.effective_uncertainty)
            mechanism_refs.append(scientific_runtime_assessment.method_version)
        return GovernanceInput(evidence_ids=base.evidence_ids, provenance_refs=tuple(dict.fromkeys(provenance_refs)), evidence_quality=base.evidence_quality, independent_evidence_ratio=base.independent_evidence_ratio, contradiction_ratio=base.contradiction_ratio, credibility=base.credibility, mechanism_satisfied=mechanism_satisfied, manipulation_flags=base.manipulation_flags, collusion_flags=base.collusion_flags, provenance_valid=base.provenance_valid, mechanism_integrity_valid=base.mechanism_integrity_valid, model_conflict=merged_model_conflict, uncertainty=min(1.0, merged_uncertainty), response_closure_complete=base.response_closure_complete, scientific_findings=tuple(dict.fromkeys(findings)), code_revision=base.code_revision, configuration_hash=base.configuration_hash, mechanism_ref="+".join(x for x in mechanism_refs if x))

    def execute(self, context: DecisionContext, options: Sequence[DecisionOption], evidence: Sequence[DecisionEvidence], *, state_refs: Sequence[str], signal_refs: Sequence[str] = (), inference_refs: Sequence[str] = (), hypothesis_refs: Sequence[str] = (), model_refs: Sequence[str] = (), prediction_refs: Sequence[str] = (), scenario_refs: Sequence[str] = (), assumption_refs: Sequence[str] = (), transformation_refs: Sequence[str] = (), constraint_refs: Sequence[str] = (), conflict_resolutions: Sequence[ConflictResolution] = (), purpose: str, restricted: bool = False, boundaries: Sequence[InformationBoundary] = (), output_visibility: InformationVisibility = InformationVisibility.PUBLIC, mode: DecisionMode = DecisionMode.ROBUST, at: datetime | None = None, state_available: bool = True, model_releases: Mapping[str, ModelGovernanceRecord] | None = None, scientific_governance_input: GovernanceInput | None = None, response_closure_complete: bool = True, nonstationarity_assessment: NonStationarityAssessment | None = None, scientific_runtime_assessment: ScientificRuntimeAssessment | None = None, validation_observation: ValidationObservation | None = None) -> DecisionLifecycleResult:
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
        model_releases = model_releases or {}
        model_reasons: list[str] = []
        for model_ref in model_refs:
            release = model_releases.get(model_ref)
            if release is None or not release.calibrated or not self.model_governance.validate(release, timestamp):
                model_reasons.append(f"model release unavailable, uncalibrated or outside validity: {model_ref}")
        conflicts = tuple(conflict_resolutions)
        manifest = self._manifest(context, evidence, state_refs, hypothesis_refs, model_refs, scenario_refs, assumption_refs, transformation_refs, constraint_refs)
        uncertainty = UncertaintyState(max((item.assessment.adversarial_risk for item in evidence), default=1.0 if not evidence else 0.0), source_refs=tuple(item.evidence_id for item in evidence), method="evidence-adversarial-risk-conservative-max")
        degraded = self._degraded_reasons(evidence, state_available=state_available, models_available=not model_reasons, persistence_available=True)
        if model_reasons:
            degraded = (*degraded, *model_reasons)
        governance_signal: GovernanceSignal | None = None
        if evidence and state_available and not model_reasons:
            governance_signal = self.scientific_governance.evaluate(context.decision_id, self._governance_input(evidence, conflicts, uncertainty=uncertainty.value, model_conflict=bool(model_reasons), mechanism_input=scientific_governance_input, response_closure_complete=response_closure_complete, decision_id=context.decision_id, nonstationarity=nonstationarity_assessment, scientific_runtime_assessment=scientific_runtime_assessment, validation_observation=validation_observation), created_at=timestamp)
            degraded = (*degraded, *(f"governance:{reason.value}" for reason in governance_signal.reasons if reason.value != "integrity_verified"))
        else:
            degraded = (*degraded, "scientific governance cannot release degraded execution")
        force_abstain = governance_signal is None or governance_signal.disposition is GovernanceDisposition.ABSTAIN
        force_review = governance_signal is not None and governance_signal.disposition is GovernanceDisposition.REVIEW_REQUIRED
        if not evidence or not state_available or model_reasons or force_abstain:
            control = self.control.authorize(decision_id=context.decision_id, purpose=purpose, uncertainty=UncertaintyState(1.0, source_refs=tuple(item.evidence_id for item in evidence), method="degraded-mode"), restricted=restricted, manifest=manifest, evidence_assessments=assessments, conflict_resolutions=conflicts)
            reason = "; ".join(degraded) or (governance_signal.effect if governance_signal else "scientific governance abstained")
            recommendation = self.decisions._abstain(context, mode, reason, (f"audit:{control.audit_event_id}",), ("reevaluate after recovery",))
        else:
            control = self.control.authorize(decision_id=context.decision_id, purpose=purpose, uncertainty=uncertainty, restricted=restricted, manifest=manifest, evidence_assessments=assessments, conflict_resolutions=conflicts)
            provenance = tuple([f"evidence:{item.evidence_id}" for item in evidence] + [f"signal:{ref}" for ref in signal_refs] + [f"inference:{ref}" for ref in inference_refs] + [f"hypothesis:{ref}" for ref in hypothesis_refs] + [f"prediction:{ref}" for ref in prediction_refs] + [f"model:{ref}" for ref in model_refs] + ([f"governance:{governance_signal.signal_id}"] if governance_signal else []) + ([f"nonstationarity:{nonstationarity_assessment.evidence_fingerprint}"] if nonstationarity_assessment else []) + ([f"scientific-runtime:{scientific_runtime_assessment.assessment_id}"] if scientific_runtime_assessment else []) + ([f"intervention-validation:{validation_observation.observation_id}"] if validation_observation else []) + [f"audit:{control.audit_event_id"])
            if control.disposition in {DecisionDisposition.ABSTAIN, DecisionDisposition.BLOCK}:
                recommendation = self.decisions._abstain(context, mode, control.reason, provenance, ("reevaluate after new evidence",))
            elif control.disposition is DecisionDisposition.HUMAN_REVIEW or force_review:
                recommendation = self.decisions._abstain(context, mode, "scientific governance requires human review" if force_review else "human review required before execution", provenance, ("reevaluate after human disposition",))
            else:
                recommendation = self.decisions.recommend(context, options, mode=mode, provenance=provenance, reevaluation_triggers=("reevaluate after new evidence", "material state change", "model validity change", "governance signal change", "non-stationary regime change", "reference-class applicability change", "deployment support boundary change", "causal identification change", "intervention validation outcome"), at=timestamp)
        terminal = recommendation.disposition.value
        governance_refs = (governance_signal.signal_id,) if governance_signal else ()
        scientific_refs = (f"scientific-runtime:{scientific_runtime_assessment.assessment_id}",) if scientific_runtime_assessment else ()
        validation_refs = (f"intervention-validation:{validation_observation.observation_id}",) if validation_observation else ()
        nonstationarity_refs = (f"nonstationarity:{nonstationarity_assessment.evidence_fingerprint}",) if nonstationarity_assessment else ()
        prediction_refs = tuple(prediction_refs)
        nodes = (
            LineageNode(f"{context.decision_id}:evidence", "evidence", evidence_refs=tuple(item.evidence_id for item in evidence), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:state", "state", input_refs=tuple(item.evidence_id for item in evidence), output_refs=tuple(state_refs), evidence_refs=tuple(item.evidence_id for item in evidence), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:prediction", "prediction", input_refs=prediction_refs, output_refs=prediction_refs, evidence_refs=tuple(item.evidence_id for item in evidence), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:analysis", "analysis", input_refs=tuple(state_refs) + prediction_refs, output_refs=tuple(signal_refs) + tuple(inference_refs) + tuple(hypothesis_refs), evidence_refs=tuple(item.evidence_id for item in evidence), model_refs=tuple(model_refs), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:scientific", "scientific_governance", input_refs=scientific_refs + validation_refs + nonstationarity_refs + governance_refs + prediction_refs, output_refs=scientific_refs + validation_refs + nonstationarity_refs + governance_refs, evidence_refs=tuple(item.evidence_id for item in evidence), model_refs=tuple(model_refs), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
            LineageNode(f"{context.decision_id}:decision", "decision", input_refs=tuple(scenario_refs) + tuple(hypothesis_refs) + governance_refs + scientific_refs + validation_refs + nonstationarity_refs + prediction_refs, output_refs=(context.decision_id, recommendation.option_id), evidence_refs=tuple(item.evidence_id for item in evidence), model_refs=tuple(model_refs), policy_refs=(manifest.policy_version,), configuration_hash=manifest.configuration_hash, code_revision=self.code_revision, as_of=manifest.created_at),
        )
        lineage = DecisionLineage(context.decision_id, nodes, terminal, manifest.fingerprint())
        self.store.record_lineage(lineage)
        self.store.record_cycle(system_id="ceutia", as_of=manifest.created_at, decision_id=context.decision_id, option_id=recommendation.option_id, disposition=terminal, lineage=tuple(node.node_id for node in nodes), stages=tuple({"stage": node.stage, "inputs": node.input_refs, "outputs": node.output_refs} for node in nodes))
        return DecisionLifecycleResult(context.decision_id, recommendation.disposition, recommendation, control.reason, control.audit_event_id, lineage, uncertainty, tuple(degraded), governance_signal)


@dataclass(frozen=True, slots=True)
class _LifecyclePolicy:
    base: ReviewPolicy
    version: str

    def evaluate(self, *, purpose: str, uncertainty: float, restricted: bool):
        from app.core.decision.control_plane import PolicyDecision
        if restricted:
            return PolicyDecision(False, False, "restricted information requires an authorized policy path", self.version)
        disposition = self.base.disposition(DecisionRisk.CRITICAL if uncertainty >= 1.0 else DecisionRisk.HIGH if uncertainty >= 0.75 else DecisionRisk.MODERATE if uncertainty >= 0.5 else DecisionRisk.LOW)
        return PolicyDecision(disposition is ReviewDisposition.AUTO, disposition is ReviewDisposition.HUMAN_REVIEW, f"risk policy {self.version}: {disposition.value}", self.version)


__all__ = ["BitemporalRef", "DecisionEvidence", "DecisionSignal", "DecisionInference", "DecisionHypothesis", "DecisionPrediction", "DecisionLifecycleEngine", "DecisionLifecycleResult"]
