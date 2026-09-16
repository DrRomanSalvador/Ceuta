"""Executable scientific contracts for cumulative CeutIA/SERPIENTE integration.

This module deliberately preserves multidimensional evidence, temporal semantics,
epistemic state and decision lineage instead of collapsing them into a single score.
It is a contract layer: it does not claim prospective/scientific validity merely by
constructing an object.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from math import isfinite
from typing import Mapping


class EvidenceLevel(IntEnum):
    E0_DATA_EXISTENCE = 0
    E1_REPRODUCIBLE_MEASUREMENT = 1
    E2_DESCRIPTIVE_PATTERN = 2
    E3_PREDICTIVE_ASSOCIATION = 3
    E4_LATENT_STATE = 4
    E5_MECHANISM = 5
    E6_CAUSAL_EFFECT = 6
    E7_DECISIONAL_UTILITY = 7
    E8_PREVENTION = 8


class EpistemicState(StrEnum):
    OBSERVATION = "OBSERVATION"
    MEASUREMENT = "MEASUREMENT"
    EVIDENCE = "EVIDENCE"
    DESCRIPTION = "DESCRIPTION"
    SIGNAL = "SIGNAL"
    ASSOCIATION = "ASSOCIATION"
    PREDICTION = "PREDICTION"
    HYPOTHESIS = "HYPOTHESIS"
    MODEL = "MODEL"
    PROPOSED_MECHANISM = "PROPOSED_MECHANISM"
    CAUSAL_EFFECT = "CAUSAL_EFFECT"
    DECISION = "DECISION"
    INTERVENTION = "INTERVENTION"
    OUTCOME = "OUTCOME"
    EVALUATION = "EVALUATION"
    PROVISIONAL_KNOWLEDGE = "PROVISIONAL_KNOWLEDGE"
    REPLICATED_KNOWLEDGE = "REPLICATED_KNOWLEDGE"
    REJECTED = "REJECTED"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"
    OUTDATED = "OUTDATED"


class KnowledgeStatus(StrEnum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"
    ESTIMATED = "ESTIMATED"
    VALIDATED = "VALIDATED"
    PROVISIONAL = "PROVISIONAL"


class Identifiability(StrEnum):
    IDENTIFIABLE = "IDENTIFIABLE"
    PARTIALLY_IDENTIFIABLE = "PARTIALLY_IDENTIFIABLE"
    NON_IDENTIFIABLE = "NON_IDENTIFIABLE"
    UNKNOWN = "UNKNOWN"


class ScientificConsequence(StrEnum):
    NO_CHANGE = "NO_CHANGE"
    CLAIM_STRENGTHENED = "CLAIM_STRENGTHENED"
    CLAIM_WEAKENED = "CLAIM_WEAKENED"
    CLAIM_REJECTED = "CLAIM_REJECTED"
    MODEL_IMPROVED = "MODEL_IMPROVED"
    MODEL_REJECTED = "MODEL_REJECTED"
    HYPOTHESIS_SUPPORTED = "HYPOTHESIS_SUPPORTED"
    HYPOTHESIS_REFUTED = "HYPOTHESIS_REFUTED"
    NEW_HYPOTHESIS = "NEW_HYPOTHESIS"
    ONTOLOGY_CHANGE = "ONTOLOGY_CHANGE"
    DATA_REQUIREMENT = "DATA_REQUIREMENT"
    NEW_VALIDATION_REQUIREMENT = "NEW_VALIDATION_REQUIREMENT"
    DECISION_RULE_CHANGED = "DECISION_RULE_CHANGED"


class CapabilityStatus(StrEnum):
    NOT_DESIGNED = "NOT_DESIGNED"
    DESIGNED = "DESIGNED"
    IMPLEMENTED = "IMPLEMENTED"
    TESTED = "TESTED"
    VALIDATED = "VALIDATED"
    PROSPECTIVELY_VALIDATED = "PROSPECTIVELY_VALIDATED"
    EXTERNALLY_VALIDATED = "EXTERNALLY_VALIDATED"
    OPERATIONALLY_VALIDATED = "OPERATIONALLY_VALIDATED"


class ScientificDebtType(StrEnum):
    DATA_DEBT = "DATA_DEBT"
    MEASUREMENT_DEBT = "MEASUREMENT_DEBT"
    STATISTICAL_DEBT = "STATISTICAL_DEBT"
    VALIDATION_DEBT = "VALIDATION_DEBT"
    CAUSAL_DEBT = "CAUSAL_DEBT"
    MODEL_DEBT = "MODEL_DEBT"
    PROVENANCE_DEBT = "PROVENANCE_DEBT"
    EPISTEMOLOGICAL_DEBT = "EPISTEMOLOGICAL_DEBT"
    DECISIONAL_DEBT = "DECISIONAL_DEBT"
    GOVERNANCE_DEBT = "GOVERNANCE_DEBT"


@dataclass(frozen=True, slots=True)
class DimensionAssessment:
    status: KnowledgeStatus
    value: float | None = None
    rationale: str = ""

    def __post_init__(self) -> None:
        if self.value is not None and (not isfinite(self.value) or not 0.0 <= self.value <= 1.0):
            raise ValueError("dimension value must be finite and in [0,1]")
        if self.status is KnowledgeStatus.UNKNOWN and self.value is not None:
            raise ValueError("UNKNOWN dimensions cannot carry a value")


@dataclass(frozen=True, slots=True)
class EvidenceAssessment:
    certainty: DimensionAssessment
    external_validity: DimensionAssessment
    actionability: DimensionAssessment
    residual_uncertainty: DimensionAssessment

    def scalar(self) -> None:
        """Evidence dimensions are intentionally non-collapsible."""
        return None


@dataclass(frozen=True, slots=True)
class TemporalSemantics:
    event_time: str
    observation_time: str
    publication_time: str
    ingestion_time: str
    revision_time: str
    availability_time: str
    forecast_origin: str | None = None
    forecast_horizon: str | None = None
    outcome_time: str | None = None
    decision_time: str | None = None
    intervention_time: str | None = None

    def __post_init__(self) -> None:
        required = (self.event_time, self.observation_time, self.publication_time,
                    self.ingestion_time, self.revision_time, self.availability_time)
        if any(not value.strip() for value in required):
            raise ValueError("all core temporal semantics are required")


@dataclass(frozen=True, slots=True)
class ObservationProcessModel:
    equation: str
    observable_variables: tuple[str, ...]
    latent_variables: tuple[str, ...]
    parameters: tuple[str, ...]
    assumptions: tuple[str, ...]
    identifiability: Identifiability
    validation_plan: tuple[str, ...]
    failure_modes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.equation.strip() or not self.assumptions or not self.validation_plan:
            raise ValueError("observation-process model requires equation, assumptions and validation")


@dataclass(frozen=True, slots=True)
class ClaimContract:
    claim_id: str
    claim_type: str
    claim_text: str
    scope: str
    geography: str
    population: str
    time_window: str
    source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    model_ids: tuple[str, ...]
    hypothesis_ids: tuple[str, ...]
    alternatives: tuple[str, ...]
    assumptions: tuple[str, ...]
    identifiability_status: Identifiability
    evidence_level: EvidenceLevel
    certainty: DimensionAssessment
    external_validity: DimensionAssessment
    calibration_status: KnowledgeStatus
    decision_relevance: KnowledgeStatus
    actionability: DimensionAssessment
    failure_modes: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]
    expiry_condition: str
    review_date: str
    responsible_mission: str
    epistemic_state: EpistemicState

    def __post_init__(self) -> None:
        if not self.claim_id or not self.claim_text or not self.responsible_mission:
            raise ValueError("claim identity/text/owner are required")
        if self.evidence_level >= EvidenceLevel.E3 and not self.evidence_ids:
            raise ValueError("predictive-or-stronger claims require evidence identifiers")
        if self.evidence_level >= EvidenceLevel.E6 and self.identifiability_status is Identifiability.NON_IDENTIFIABLE:
            raise ValueError("causal claims cannot be non-identifiable")


@dataclass(frozen=True, slots=True)
class HypothesisContract:
    hypothesis_id: str
    originating_evidence: tuple[str, ...]
    phenomenon: str
    mechanism_claim: str
    alternatives: tuple[str, ...]
    predicted_observations: tuple[str, ...]
    disconfirming_observations: tuple[str, ...]
    required_data: tuple[str, ...]
    analysis_plan: tuple[str, ...]
    stopping_rule: str
    external_validation_plan: tuple[str, ...]
    status: str
    exploratory: bool = True
    frozen: bool = False

    def __post_init__(self) -> None:
        if not self.hypothesis_id or not self.originating_evidence or not self.disconfirming_observations:
            raise ValueError("hypothesis requires provenance and falsification criteria")
        if not self.stopping_rule.strip():
            raise ValueError("hypothesis requires a stopping rule")
        if not self.exploratory and not self.frozen:
            raise ValueError("confirmatory hypotheses must be frozen")


@dataclass(frozen=True, slots=True)
class PredictionContract:
    prediction_id: str
    information_cutoff: str
    observation_vintage: str
    feature_availability: Mapping[str, str]
    forecast_origin: str
    forecast_horizon: str
    model_version: str
    target_definition: str
    outcome_definition: str
    point_in_time_fingerprint: str
    provenance_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.prediction_id, self.information_cutoff, self.observation_vintage,
                    self.forecast_origin, self.forecast_horizon, self.model_version,
                    self.target_definition, self.outcome_definition,
                    self.point_in_time_fingerprint)):
            raise ValueError("prediction contract is incomplete")
        if not self.feature_availability or not self.provenance_ids:
            raise ValueError("prediction requires feature availability and provenance")


@dataclass(frozen=True, slots=True)
class DecisionContract:
    decision_id: str
    decision_target: str
    decision_maker: str
    available_actions: tuple[str, ...]
    loss_function: str
    false_positive_cost: str
    false_negative_cost: str
    time_constraint: str
    reversibility: str
    uncertainty: tuple[str, ...]
    withdrawal_condition: str
    prediction_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.decision_id or not self.decision_target or not self.decision_maker:
            raise ValueError("decision identity/target/maker are required")
        if not self.available_actions or not self.loss_function or not self.withdrawal_condition:
            raise ValueError("decision requires actions, loss function and withdrawal condition")


@dataclass(frozen=True, slots=True)
class InterventionContract:
    intervention_id: str
    target: str
    decision_id: str
    start_time: str
    end_time: str | None
    population: str
    exposure: str
    responsible_actor: str
    intended_effect: str
    possible_harms: tuple[str, ...]
    concurrent_interventions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OutcomeContract:
    outcome_id: str
    intervention_id: str
    definition: str
    window: str
    population: str
    measurement: str
    exposure: str
    censoring: str
    missingness: str
    concurrent_interventions: tuple[str, ...]
    adverse_effects: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ModelContract:
    model_id: str
    version: str
    equation_or_algorithm: str
    parameters: tuple[str, ...]
    training_data_vintage: str
    validation_data_vintage: str
    information_cutoff: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    benchmark_ids: tuple[str, ...]
    calibration_status: KnowledgeStatus
    external_validation_status: KnowledgeStatus
    deployment_state: str
    retirement_condition: str
    rollback_condition: str
    change_history: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScientificDebt:
    debt_id: str
    debt_type: ScientificDebtType
    affected_object: str
    severity: str
    scientific_consequence: str
    decision_consequence: str
    blocking_status: bool
    owner: str
    created_at: str
    review_at: str
    resolution: str | None = None


@dataclass(frozen=True, slots=True)
class DossierItem:
    dossier_item_id: str
    source_reference: str
    scientific_proposition: str
    evidence_type: str
    mathematical_component: str
    architectural_component: str
    current_repo_support: str
    gap: str
    action: str
    implementation_status: str
    validation_status: str
    test_status: str
    responsible_component: str
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    rejection_reason: str | None = None
    relation_to_prior: str = "NEW"


def promotion_allowed(current: EvidenceLevel, target: EvidenceLevel, requirements: Mapping[str, bool]) -> bool:
    """Allow only adjacent epistemic promotion with explicit gate evidence."""
    if target.value != current.value + 1:
        return False
    return bool(requirements) and all(bool(value) for value in requirements.values())


def claim_strength_is_bounded(claim: ClaimContract, available_level: EvidenceLevel) -> bool:
    return claim.evidence_level <= available_level


__all__ = [
    "CapabilityStatus", "ClaimContract", "DecisionContract", "DimensionAssessment",
    "DossierItem", "EpistemicState", "EvidenceAssessment", "EvidenceLevel",
    "HypothesisContract", "Identifiability", "InterventionContract", "KnowledgeStatus",
    "ModelContract", "ObservationProcessModel", "OutcomeContract", "PredictionContract",
    "ScientificConsequence", "ScientificDebt", "ScientificDebtType", "TemporalSemantics",
    "claim_strength_is_bounded", "promotion_allowed",
]
