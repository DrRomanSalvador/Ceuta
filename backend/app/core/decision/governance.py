from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Actionability(str, Enum):
    OBSERVATIONAL = "observational"
    INTERVENTIONAL = "interventional"


@dataclass(frozen=True, slots=True)
class InterventionSpec:
    action_id: str
    actionability: Actionability
    target: str
    intervention: str
    causal_model_ref: str
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all((self.action_id, self.target, self.intervention, self.causal_model_ref)):
            raise ValueError("intervention requires action, target, intervention and causal model reference")


@dataclass(frozen=True, slots=True)
class DecisionProvenance:
    decision_id: str
    model_refs: tuple[str, ...]
    hypothesis_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    transformation_refs: tuple[str, ...]
    assumption_refs: tuple[str, ...]
    scenario_refs: tuple[str, ...]
    utility_definition_ref: str
    constraint_refs: tuple[str, ...]

    def complete(self) -> bool:
        return bool(
            self.decision_id
            and self.model_refs
            and self.evidence_refs
            and self.scenario_refs
            and self.utility_definition_ref
        )


@dataclass(frozen=True, slots=True)
class ReevaluationPolicy:
    valid_until: str
    triggers: tuple[str, ...]
    minimum_evidence_change: float = 0.0

    def __post_init__(self) -> None:
        if not self.valid_until or self.minimum_evidence_change < 0:
            raise ValueError("invalid reevaluation policy")


@dataclass(frozen=True, slots=True)
class DecisionFeedbackRecord:
    decision_id: str
    option_id: str
    expected: Mapping[str, float]
    observed: Mapping[str, float]

    def errors(self) -> Mapping[str, float]:
        keys = set(self.expected) | set(self.observed)
        return {key: float(self.observed.get(key, 0.0)) - float(self.expected.get(key, 0.0)) for key in keys}


@dataclass(frozen=True, slots=True)
class DecisionGovernance:
    require_human_review_above_uncertainty: float = 0.35
    require_abstention_above_uncertainty: float = 0.75
    allow_autonomous_intervention: bool = False

    def disposition(self, uncertainty: float) -> str:
        if not 0 <= uncertainty <= 1:
            raise ValueError("uncertainty must be in [0, 1]")
        if uncertainty >= self.require_abstention_above_uncertainty:
            return "ABSTAIN"
        if uncertainty >= self.require_human_review_above_uncertainty:
            return "HUMAN_REVIEW"
        return "RECOMMEND"
