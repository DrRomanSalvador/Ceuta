"""Closed-loop intervention and response attribution contracts."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

@dataclass(frozen=True, slots=True)
class InterventionExecution:
    intervention_id: str
    planned_at: datetime
    delivered_at: datetime
    dose: Mapping[str,float]
    target_ids: tuple[str,...]
    fidelity: float
    decision_id: str

@dataclass(frozen=True, slots=True)
class ResponseAssessment:
    intervention_id: str
    response_at: datetime
    observed_change: Mapping[str,float]
    reference_change: Mapping[str,float]
    attribution_status: str
    confounders: tuple[str,...]=()
    adverse_signals: tuple[str,...]=()

class InterventionResponseEngine:
    def assess(self, execution: InterventionExecution, response_at: datetime, observed: Mapping[str,float], reference: Mapping[str,float], *, confounders: tuple[str,...]=(), adverse_signals: tuple[str,...]=()) -> ResponseAssessment:
        keys=set(observed)|set(reference)
        change={k: observed.get(k,0.0)-reference.get(k,0.0) for k in keys}
        status="causal_effect_not_identified" if confounders else "response_difference_only"
        return ResponseAssessment(execution.intervention_id,response_at,change,dict(reference),status,confounders,adverse_signals)
