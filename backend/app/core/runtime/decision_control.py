"""Decision control-plane: action space, human review, triggers and audit."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence
from .risk_escalation import Escalation

@dataclass(frozen=True, slots=True)
class HumanReview:
    required: bool
    reason: str
    deadline: datetime | None = None

@dataclass(frozen=True, slots=True)
class ReassessmentTrigger:
    trigger_id: str
    condition: str
    priority: int

@dataclass(frozen=True, slots=True)
class DecisionAudit:
    decision_id: str
    state_id: str
    evidence_ids: tuple[str,...]
    model_ids: tuple[str,...]
    assumptions: tuple[str,...]
    uncertainty: float
    escalation: Escalation
    review: HumanReview
    triggers: tuple[ReassessmentTrigger,...]

class DecisionControlPlane:
    def audit(self, decision_id:str, state_id:str, evidence_ids:Sequence[str], model_ids:Sequence[str], assumptions:Sequence[str], uncertainty:float, escalation:Escalation, *, review_reason:str="", review_deadline:datetime|None=None, triggers:Sequence[ReassessmentTrigger]=())->DecisionAudit:
        if not decision_id or not state_id: raise ValueError("decision and state identities are required")
        if not 0<=uncertainty<=1: raise ValueError("uncertainty must be in [0,1]")
        required=escalation in {Escalation.ABSTAIN,Escalation.CRITICAL} or bool(review_reason)
        review=HumanReview(required,review_reason or "risk/epistemic gate" if required else "not required",review_deadline)
        return DecisionAudit(decision_id,state_id,tuple(evidence_ids),tuple(model_ids),tuple(assumptions),uncertainty,escalation,review,tuple(sorted(triggers,key=lambda x:-x.priority)))
