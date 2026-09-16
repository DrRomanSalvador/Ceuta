"""Decision-relevant uncertainty, research-priority and scientific-debt contracts."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class Identifiability(StrEnum):
    IDENTIFIABLE = "IDENTIFIABLE"
    PARTIALLY_IDENTIFIABLE = "PARTIALLY_IDENTIFIABLE"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"
    UNKNOWN = "UNKNOWN"


class ResearchPriority(StrEnum):
    T1_DECISION_CRITICAL_UNCERTAINTY = "T1"
    T2_CAPABILITY_VALIDATION = "T2"
    T3_CONTRADICTION_SEEKING = "T3"
    T4_MEASUREMENT_REPAIR = "T4"
    T5_NOVELTY_EXPLORATION = "T5"


class ValidationLayer(StrEnum):
    SOFTWARE_CORRECTNESS = "SOFTWARE_CORRECTNESS"
    DATA_INTEGRITY = "DATA_INTEGRITY"
    STATISTICAL_VALIDITY = "STATISTICAL_VALIDITY"
    PREDICTIVE_VALIDITY = "PREDICTIVE_VALIDITY"
    EXTERNAL_VALIDITY = "EXTERNAL_VALIDITY"
    CAUSAL_VALIDITY = "CAUSAL_VALIDITY"
    DECISION_VALIDITY = "DECISION_VALIDITY"
    EFFECTIVENESS = "EFFECTIVENESS"
    EQUITY = "EQUITY"


@dataclass(frozen=True, slots=True)
class VOIInputs:
    decision_id: str
    uncertainty_target: str
    utility_definition: str | None
    research_cost: float | None
    delay_cost: float | None
    risk_cost: float | None
    prior_identifiability: Identifiability

    @property
    def identifiable(self) -> bool:
        values = (self.utility_definition, self.research_cost, self.delay_cost, self.risk_cost)
        return bool(self.decision_id and self.uncertainty_target and all(value is not None for value in values) and all(isfinite(float(value)) for value in values if value is not None)) and self.prior_identifiability is not Identifiability.NOT_IDENTIFIABLE

    @property
    def status(self) -> str:
        return "IDENTIFIABLE" if self.identifiable else "NVOI_NOT_IDENTIFIABLE"


@dataclass(frozen=True, slots=True)
class InvestigationTaskContract:
    task_id: str
    uncertainty_target: str
    decision_relevance: str
    possible_decision_change: str
    discriminating_result: str
    research_cost: str
    delay_cost: str
    risk: str
    stopping_rule: str
    bias_risks: tuple[str, ...]
    priority: ResearchPriority

    def __post_init__(self) -> None:
        if not all((self.task_id, self.uncertainty_target, self.decision_relevance, self.possible_decision_change, self.discriminating_result, self.stopping_rule)):
            raise ValueError("investigation task is incomplete")


@dataclass(frozen=True, slots=True)
class VariableSemantics:
    variable_id: str
    definition: str
    unit: str
    population: str
    geography: str
    time_semantics: str
    observation_process: str
    denominator: str
    missingness: str
    uncertainty: str
    source: str
    transformation: str


@dataclass(frozen=True, slots=True)
class ScientificDebtRecord:
    debt_id: str
    debt_type: str
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
class ValidationAssessment:
    layer: ValidationLayer
    status: str
    evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status in {"VALIDATED", "PASS"} and not self.evidence_ids:
            raise ValueError("a validated layer requires evidence identifiers")


__all__ = [
    "Identifiability", "InvestigationTaskContract", "ResearchPriority", "ScientificDebtRecord",
    "VOIInputs", "ValidationAssessment", "ValidationLayer", "VariableSemantics",
]
