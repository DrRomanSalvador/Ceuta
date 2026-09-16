"""Governed evidence-to-actionability contract for CEUTIA PERSONA and ESTADO.

This is a semantic/orchestration contract, not a second decision engine.
Decision ranking remains in the existing decision subsystem.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from math import isfinite
from typing import Mapping


class ActionabilityClient(StrEnum):
    PERSONA = "PERSONA"
    ESTADO = "ESTADO"


class ActionabilityStatus(StrEnum):
    NON_ACTIONABLE = "NON_ACTIONABLE"
    CONTEXTUALLY_ACTIONABLE = "CONTEXTUALLY_ACTIONABLE"
    CONDITIONALLY_ACTIONABLE = "CONDITIONALLY_ACTIONABLE"
    DECISION_SUPPORTING = "DECISION_SUPPORTING"
    INTERVENTION_RELEVANT = "INTERVENTION_RELEVANT"
    OPERATIONALLY_ACTIONABLE = "OPERATIONALLY_ACTIONABLE"
    PROSPECTIVELY_EVALUABLE = "PROSPECTIVELY_EVALUABLE"
    OUTCOME_VALIDATED = "OUTCOME_VALIDATED"


class ProbabilityStatus(StrEnum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    UNCALIBRATED = "UNCALIBRATED"
    CALIBRATED = "CALIBRATED"


@dataclass(frozen=True, slots=True)
class ActionabilityOption:
    """Candidate action, never an authorization to execute it."""

    option_id: str
    description: str
    target: str
    mechanism: str
    expected_effect: str
    required_resources: tuple[str, ...] = ()
    time_to_effect: str = ""
    risks: tuple[str, ...] = ()
    reversibility: str = "unknown"
    implementation_constraints: tuple[str, ...] = ()
    monitoring_requirements: tuple[str, ...] = ()
    withdrawal_conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("option_id", "description", "target", "mechanism", "expected_effect"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} is required")


@dataclass(frozen=True, slots=True)
class ActionabilityAssessment:
    """Traceable actionability state shared by PERSONA and ESTADO.

    The contract records contextualized decision support. It never selects,
    authorizes, executes, or declares efficacy of an intervention.
    """

    assessment_id: str
    client_type: ActionabilityClient
    subject_or_territory: str
    problem_definition: str
    population_scope: str
    denominator_id: str | None
    evidence_refs: tuple[str, ...]
    evidence_level: str
    applicability_status: str
    applicability_reasons: tuple[str, ...]
    risk_state: str
    risk_probability: float | None
    risk_probability_status: ProbabilityStatus
    risk_uncertainty: float
    consequence: str
    exposure: str
    time_horizon: str
    alternative_explanations: tuple[str, ...]
    options: tuple[ActionabilityOption, ...]
    resource_requirements: tuple[str, ...]
    potential_harms: tuple[str, ...]
    reversibility: str
    recommended_next_step: str | None
    decision_authority: str | None
    activation_triggers: tuple[str, ...]
    withdrawal_triggers: tuple[str, ...]
    monitoring_indicators: tuple[str, ...]
    outcome_definition: str | None
    evaluation_plan: str | None
    provenance: tuple[str, ...]
    created_at: datetime
    information_cutoff: datetime
    expiry: datetime | None
    status: ActionabilityStatus
    event_time: datetime | None = None
    observation_time: datetime | None = None
    publication_time: datetime | None = None
    revision_time: datetime | None = None
    ingestion_time: datetime | None = None
    forecast_horizon: str | None = None
    intervention_window: str | None = None
    outcome_window: str | None = None
    alternative_decision_refs: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "assessment_id": self.assessment_id,
            "subject_or_territory": self.subject_or_territory,
            "problem_definition": self.problem_definition,
            "population_scope": self.population_scope,
            "evidence_level": self.evidence_level,
            "risk_state": self.risk_state,
            "consequence": self.consequence,
            "exposure": self.exposure,
            "time_horizon": self.time_horizon,
        }
        for name, value in required.items():
            if not value.strip():
                raise ValueError(f"{name} is required")
        if not self.evidence_refs:
            raise ValueError("at least one evidence reference is required")
        if not self.provenance:
            raise ValueError("provenance is required")
        if not isfinite(self.risk_uncertainty) or not 0.0 <= self.risk_uncertainty <= 1.0:
            raise ValueError("risk_uncertainty must be finite and in [0, 1]")
        if self.risk_probability is not None:
            if not isfinite(self.risk_probability) or not 0.0 <= self.risk_probability <= 1.0:
                raise ValueError("risk_probability must be finite and in [0, 1]")
            if self.risk_probability_status is not ProbabilityStatus.CALIBRATED:
                raise ValueError("risk_probability requires CALIBRATED probability status")
        elif self.risk_probability_status is ProbabilityStatus.CALIBRATED:
            raise ValueError("CALIBRATED probability status requires risk_probability")
        if self.information_cutoff > self.created_at:
            raise ValueError("information_cutoff cannot be later than assessment creation")
        if self.expiry is not None and self.expiry <= self.created_at:
            raise ValueError("expiry must be later than assessment creation")
        self._validate_timestamps()
        if self.client_type is ActionabilityClient.ESTADO and not self.denominator_id:
            raise ValueError("ESTADO assessments require an explicit denominator_id")
        if self.status in {
            ActionabilityStatus.INTERVENTION_RELEVANT,
            ActionabilityStatus.OPERATIONALLY_ACTIONABLE,
            ActionabilityStatus.PROSPECTIVELY_EVALUABLE,
            ActionabilityStatus.OUTCOME_VALIDATED,
        } and (not self.outcome_definition or not self.evaluation_plan):
            raise ValueError("intervention-relevant or stronger status requires outcome and evaluation definitions")
        if self.status in {
            ActionabilityStatus.OPERATIONALLY_ACTIONABLE,
            ActionabilityStatus.PROSPECTIVELY_EVALUABLE,
            ActionabilityStatus.OUTCOME_VALIDATED,
        } and not self.decision_authority:
            raise ValueError("operationally actionable status requires explicit decision authority")

    def _validate_timestamps(self) -> None:
        """Validate timestamp shape without inventing a false total ordering.

        Event, observation, publication, revision and ingestion times have
        different semantics. A revision can legitimately occur after the
        original ingestion; an observation can precede its publication; and
        ingestion order is not a substitute for event time.
        """
        timestamps = {
            "created_at": self.created_at,
            "information_cutoff": self.information_cutoff,
            "expiry": self.expiry,
            "event_time": self.event_time,
            "observation_time": self.observation_time,
            "publication_time": self.publication_time,
            "revision_time": self.revision_time,
            "ingestion_time": self.ingestion_time,
        }
        for name, value in timestamps.items():
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"{name} must be timezone-aware")

    def is_valid_at(self, at: datetime) -> bool:
        """Return whether this assessment is temporally valid at ``at``.

        Expiry is a semantic validity boundary. A stale assessment must not
        remain claimable merely because its stored maturity status is high.
        """
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("at must be timezone-aware")
        if at < self.created_at:
            return False
        return self.expiry is None or at < self.expiry

    def can_claim_actionability(self, at: datetime | None = None) -> bool:
        """Return whether actionability may currently be claimed.

        Without ``at``, this preserves the structural maturity check. Callers
        making a current claim should provide an evaluation time so expiry is
        enforced explicitly.
        """
        if self.status is ActionabilityStatus.NON_ACTIONABLE:
            return False
        return at is None or self.is_valid_at(at)

    def requires_human_authority(self) -> bool:
        return self.decision_authority is not None

    def epistemic_summary(self) -> dict[str, object]:
        return {
            "evidence_refs": self.evidence_refs,
            "evidence_level": self.evidence_level,
            "applicability_status": self.applicability_status,
            "risk_probability": self.risk_probability,
            "risk_probability_status": self.risk_probability_status.value,
            "risk_uncertainty": self.risk_uncertainty,
            "alternative_explanations": self.alternative_explanations,
            "provenance": self.provenance,
        }


@dataclass(frozen=True, slots=True)
class ActionabilityTrace:
    """Minimum chain needed to distinguish support from observed outcome."""

    assessment_id: str
    decision_ref: str | None = None
    intervention_ref: str | None = None
    target: str | None = None
    expected_effect: str | None = None
    observed_effect: str | None = None
    outcome_ref: str | None = None
    evaluation_ref: str | None = None
    causal_status: str = "NOT_ESTABLISHED"

    def stage(self) -> str:
        if self.evaluation_ref:
            return "EVALUATED"
        if self.outcome_ref:
            return "OUTCOME_OBSERVED"
        if self.intervention_ref:
            return "INTERVENTION_RECORDED"
        if self.decision_ref:
            return "DECISION_RECORDED"
        return "ACTIONABILITY_ONLY"


def validate_actionability_chain(
    assessment: ActionabilityAssessment,
    trace: ActionabilityTrace,
) -> tuple[str, ...]:
    """Return deficiencies; never infer missing stages."""

    errors: list[str] = []
    if assessment.assessment_id != trace.assessment_id:
        errors.append("assessment/trace identity mismatch")
    if trace.intervention_ref and not trace.decision_ref:
        errors.append("intervention cannot be recorded without a decision reference")
    if trace.outcome_ref and not trace.intervention_ref:
        errors.append("outcome cannot be attributed to an intervention without intervention exposure")
    if trace.evaluation_ref and not trace.outcome_ref:
        errors.append("evaluation cannot be recorded without an observed outcome")
    if trace.causal_status == "ESTABLISHED" and not trace.evaluation_ref:
        errors.append("causal effect cannot be established without an evaluation reference")
    if assessment.status is ActionabilityStatus.OUTCOME_VALIDATED and not trace.evaluation_ref:
        errors.append("OUTCOME_VALIDATED requires an evaluation trace")
    return tuple(errors)


__all__ = [
    "ActionabilityAssessment",
    "ActionabilityClient",
    "ActionabilityOption",
    "ActionabilityStatus",
    "ActionabilityTrace",
    "ProbabilityStatus",
    "validate_actionability_chain",
]
