"""Operational contracts for the final invisible-layer controls."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Sequence


class FalsifiabilityStatus(StrEnum):
    ESTABLISHED = "established"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class EpistemicIntegrityStatus(StrEnum):
    PRESERVED = "preserved"
    WEAKENED = "weakened"
    BROKEN = "broken"
    UNKNOWN = "unknown"


class CounterfactualStatus(StrEnum):
    IDENTIFIABLE = "identifiable"
    PARTIALLY_IDENTIFIABLE = "partially_identifiable"
    UNIDENTIFIABLE = "unidentifiable"
    NOT_APPLICABLE = "not_applicable"


class OntologyStatus(StrEnum):
    NORMAL = "normal"
    ANOMALY = "anomaly"
    PERSISTENT_UNEXPLAINED_STRUCTURE = "persistent_unexplained_structure"
    ONTOLOGY_REVIEW_REQUIRED = "ontology_review_required"
    CANDIDATE_REVISION = "candidate_revision"
    VALIDATED_REVISION = "validated_revision"


class SystemValidity(StrEnum):
    SUPPORTED = "architecturally_supported"
    DOUBT = "global_validity_in_doubt"
    ABSTAIN = "epistemically_suspended"


@dataclass(frozen=True, slots=True)
class FalsificationCondition:
    condition_id: str
    target_id: str
    expected_observation: str
    falsifying_observation: str
    independent_evidence_refs: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    testable: bool = True

    def __post_init__(self) -> None:
        if not self.condition_id or not self.target_id:
            raise ValueError("falsification condition requires identity")
        if not self.expected_observation or not self.falsifying_observation:
            raise ValueError("expected and falsifying observations are required")
        if self.testable and not self.independent_evidence_refs:
            raise ValueError("testable falsification requires independent evidence")


@dataclass(frozen=True, slots=True)
class RealityAnchorAssessment:
    target_id: str
    status: FalsifiabilityStatus
    conditions: tuple[FalsificationCondition, ...]
    external_evidence_refs: tuple[str, ...]
    common_mode_dependencies: tuple[str, ...]
    divergence_score: float
    global_model_doubt: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.target_id or not isfinite(self.divergence_score) or not 0 <= self.divergence_score <= 1:
            raise ValueError("invalid reality-anchor assessment")
        if self.status is FalsifiabilityStatus.ESTABLISHED and (not self.conditions or not self.external_evidence_refs):
            raise ValueError("established reality anchoring requires falsification conditions and external evidence")
        if self.status is FalsifiabilityStatus.ESTABLISHED and self.global_model_doubt:
            raise ValueError("established reality anchoring cannot simultaneously declare global model doubt")


@dataclass(frozen=True, slots=True)
class EpistemicContract:
    contract_id: str
    semantic_meaning: str
    assumptions: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    temporal_reference: str
    spatial_reference: str | None
    denominator: str | None
    population: str | None
    identification_conditions: tuple[str, ...]
    causal_interpretation: str
    evidence_status: str
    calibration_conditions: tuple[str, ...]
    validity_domain: str
    uncertainty_semantics: str
    dependency_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = (self.contract_id, self.semantic_meaning, self.temporal_reference, self.validity_domain, self.uncertainty_semantics)
        if any(not value.strip() for value in required):
            raise ValueError("epistemic contract identity and semantics are required")
        if not self.provenance_refs:
            raise ValueError("epistemic contract requires provenance")
        if not self.uncertainty_semantics.strip():
            raise ValueError("epistemic contract requires explicit uncertainty semantics")


@dataclass(frozen=True, slots=True)
class EpistemicTransformation:
    transformation_id: str
    source_contract: EpistemicContract
    output_contract: EpistemicContract
    preserves: tuple[str, ...]
    weakens: tuple[str, ...] = ()
    breaks: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()
    introduced_dependencies: tuple[str, ...] = ()
    justification: str = ""

    @property
    def status(self) -> EpistemicIntegrityStatus:
        if self.breaks:
            return EpistemicIntegrityStatus.BROKEN
        if self.unknown:
            return EpistemicIntegrityStatus.UNKNOWN
        if self.weakens:
            return EpistemicIntegrityStatus.WEAKENED
        return EpistemicIntegrityStatus.PRESERVED

    def __post_init__(self) -> None:
        if not self.transformation_id or not self.justification:
            raise ValueError("transformation requires identity and justification")


class EpistemicIntegrityEngine:
    @staticmethod
    def aggregate(transformations: Sequence[EpistemicTransformation]) -> EpistemicIntegrityStatus:
        statuses = [item.status for item in transformations]
        if not statuses:
            return EpistemicIntegrityStatus.UNKNOWN
        if EpistemicIntegrityStatus.BROKEN in statuses:
            return EpistemicIntegrityStatus.BROKEN
        if EpistemicIntegrityStatus.UNKNOWN in statuses:
            return EpistemicIntegrityStatus.UNKNOWN
        if EpistemicIntegrityStatus.WEAKENED in statuses:
            return EpistemicIntegrityStatus.WEAKENED
        return EpistemicIntegrityStatus.PRESERVED


@dataclass(frozen=True, slots=True)
class ClosedLoopEvaluation:
    decision_id: str
    intervention_id: str | None
    observed_outcome: float
    expected_outcome: float | None
    counterfactual_status: CounterfactualStatus
    policy_induced_change: bool
    observation_process_changed: bool
    target_distribution_changed: bool
    prediction_quality_status: str
    causal_effect_status: str
    decision_quality_status: str
    contamination_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision identity is required")
        if not isfinite(self.observed_outcome) or (self.expected_outcome is not None and not isfinite(self.expected_outcome)):
            raise ValueError("closed-loop outcomes must be finite")
        if self.intervention_id is None and self.counterfactual_status is not CounterfactualStatus.NOT_APPLICABLE:
            raise ValueError("non-intervention outcome requires NOT_APPLICABLE counterfactual status")
        if self.intervention_id is not None and self.counterfactual_status is CounterfactualStatus.NOT_APPLICABLE:
            raise ValueError("intervention-conditioned outcome requires an explicit counterfactual status")


@dataclass(frozen=True, slots=True)
class OntologySignal:
    signal_id: str
    description: str
    persistence: float
    unexplained_structure: float
    cross_domain_inconsistency: float
    model_disagreement: float
    boundary_pressure: float
    new_entity_pressure: float

    def __post_init__(self) -> None:
        if not self.signal_id or not self.description:
            raise ValueError("ontology signal identity and description are required")
        values = (self.persistence, self.unexplained_structure, self.cross_domain_inconsistency, self.model_disagreement, self.boundary_pressure, self.new_entity_pressure)
        if any(not isfinite(value) or not 0 <= value <= 1 for value in values):
            raise ValueError("ontology signal scores must be finite and in [0,1]")


@dataclass(frozen=True, slots=True)
class EpistemicSelfModel:
    version: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    identification_limits: tuple[str, ...]
    ontology_status: OntologyStatus
    ontology_version: str
    unexplained_signals: tuple[OntologySignal, ...]
    global_validity: SystemValidity

    def __post_init__(self) -> None:
        if not self.version.strip() or not self.ontology_version.strip():
            raise ValueError("self-model requires versioned identity")
        if not self.assumptions or not self.limitations:
            raise ValueError("self-model requires explicit assumptions and limitations")
        if self.ontology_status is OntologyStatus.NORMAL and self.unexplained_signals:
            raise ValueError("normal ontology status cannot contain unexplained ontology signals")


class EpistemicSelfCritique:
    @staticmethod
    def assess(signals: Sequence[OntologySignal], threshold: float = 0.7) -> OntologyStatus:
        if not isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError("ontology threshold must be finite and in [0,1]")
        if not signals:
            return OntologyStatus.NORMAL
        persistent = [s for s in signals if s.persistence >= threshold]
        if not persistent:
            return OntologyStatus.ANOMALY
        strong = [s for s in persistent if max(
            s.unexplained_structure,
            s.cross_domain_inconsistency,
            s.boundary_pressure,
            s.new_entity_pressure,
        ) >= threshold]
        return OntologyStatus.ONTOLOGY_REVIEW_REQUIRED if strong else OntologyStatus.PERSISTENT_UNEXPLAINED_STRUCTURE

    @staticmethod
    def candidate_revision_allowed(status: OntologyStatus, independent_review: bool) -> bool:
        return status is OntologyStatus.ONTOLOGY_REVIEW_REQUIRED and independent_review


@dataclass(frozen=True, slots=True)
class ProspectiveEvaluationProtocol:
    protocol_id: str
    target: str
    population: str
    context: str
    horizon: str
    decision_rule: str
    comparator: str
    outcome: str
    protocol_version: str
    system_version: str
    model_version: str
    ontology_version: str
    policy_version: str
    precommitted: bool

    def __post_init__(self) -> None:
        fields = (self.protocol_id, self.target, self.population, self.context, self.horizon, self.decision_rule, self.comparator, self.outcome, self.protocol_version, self.system_version, self.model_version, self.ontology_version, self.policy_version)
        if any(not value.strip() for value in fields):
            raise ValueError("prospective protocol requires complete non-empty identifiers and definitions")
        if self.precommitted and self.decision_rule.strip().lower() in {"", "post hoc", "posthoc", "adaptive without precommitment"}:
            raise ValueError("precommitted protocol cannot use a post-hoc or explicitly non-precommitted decision rule")


@dataclass(frozen=True, slots=True)
class ProspectiveEvaluationResult:
    protocol_id: str
    observed_benefit: float | None
    deployment_validity: bool
    empirical_status: str

    def __post_init__(self) -> None:
        if not self.protocol_id.strip() or not self.empirical_status.strip():
            raise ValueError("prospective result requires protocol and empirical status")
        if self.observed_benefit is not None and not isfinite(self.observed_benefit):
            raise ValueError("observed prospective benefit must be finite")
        if self.empirical_status == "prospectively_validated" and not self.deployment_validity:
            raise ValueError("prospectively validated result requires valid deployment")


@dataclass(frozen=True, slots=True)
class FinalEpistemicAssessment:
    reality_anchor: RealityAnchorAssessment
    composition: EpistemicIntegrityStatus
    closed_loop: ClosedLoopEvaluation | None
    self_model: EpistemicSelfModel
    prospective_protocol: ProspectiveEvaluationProtocol | None
    method_effectiveness_established: bool
    validity: SystemValidity
    reasons: tuple[str, ...]


class FinalEpistemicController:
    def assess(self, *, reality_anchor: RealityAnchorAssessment,
               transformations: Sequence[EpistemicTransformation],
               self_model: EpistemicSelfModel,
               closed_loop: ClosedLoopEvaluation | None = None,
               prospective_protocol: ProspectiveEvaluationProtocol | None = None,
               prospective_result: ProspectiveEvaluationResult | None = None) -> FinalEpistemicAssessment:
        composition = EpistemicIntegrityEngine.aggregate(transformations)
        reasons = list(reality_anchor.reasons)
        validity = SystemValidity.SUPPORTED
        if reality_anchor.global_model_doubt or composition is EpistemicIntegrityStatus.BROKEN:
            validity = SystemValidity.DOUBT
        if self_model.global_validity is not SystemValidity.SUPPORTED:
            validity = self_model.global_validity
        if closed_loop and closed_loop.counterfactual_status is CounterfactualStatus.UNIDENTIFIABLE:
            reasons.append("intervention-conditioned outcome lacks an identifiable counterfactual")
        if prospective_protocol and not prospective_protocol.precommitted:
            reasons.append("prospective protocol is not precommitted")
        if prospective_result and (
            prospective_protocol is None or prospective_result.protocol_id != prospective_protocol.protocol_id
        ):
            reasons.append("prospective result is not linked to the active protocol")
        effective = bool(
            prospective_protocol
            and prospective_protocol.precommitted
            and prospective_result
            and prospective_result.protocol_id == prospective_protocol.protocol_id
            and prospective_result.deployment_validity
            and prospective_result.empirical_status == "prospectively_validated"
            and prospective_result.observed_benefit is not None
            and prospective_result.observed_benefit > 0
        )
        return FinalEpistemicAssessment(
            reality_anchor, composition, closed_loop, self_model,
            prospective_protocol, effective, validity, tuple(reasons)
        )


__all__ = [
    "ClosedLoopEvaluation", "CounterfactualStatus", "EpistemicContract",
    "EpistemicIntegrityEngine", "EpistemicIntegrityStatus", "EpistemicSelfCritique",
    "EpistemicSelfModel", "EpistemicTransformation", "FinalEpistemicAssessment",
    "FinalEpistemicController", "FalsifiabilityStatus", "FalsificationCondition",
    "OntologySignal", "OntologyStatus", "ProspectiveEvaluationProtocol",
    "ProspectiveEvaluationResult", "RealityAnchorAssessment", "SystemValidity",
]
