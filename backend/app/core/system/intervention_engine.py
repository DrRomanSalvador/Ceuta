"""Intervention as a controlled perturbation and measurable response."""
from dataclasses import dataclass
from datetime import datetime
from ..errors import ContractViolation, TemporalViolation

@dataclass(frozen=True, slots=True)
class Intervention:
    intervention_id: str
    decision_id: str
    started_at: datetime
    intended_effect: str
    target_variables: tuple[str, ...]
    def __post_init__(self):
        if self.started_at.tzinfo is None: raise TemporalViolation("intervention time must be timezone-aware")
        if not self.intervention_id or not self.decision_id or not self.target_variables: raise ContractViolation("intervention fields required")

@dataclass(frozen=True, slots=True)
class InterventionResponse:
    response_id: str
    intervention_id: str
    measured_at: datetime
    outcome_summary: str
    adverse_signals: tuple[str, ...] = ()
    causal_effect_estimated: bool = False
    def __post_init__(self):
        if self.measured_at.tzinfo is None: raise TemporalViolation("response time must be timezone-aware")
        if not self.response_id or not self.intervention_id: raise ContractViolation("response IDs required")
