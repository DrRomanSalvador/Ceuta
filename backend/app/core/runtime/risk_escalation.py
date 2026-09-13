"""Evidence-gated escalation states for longitudinal monitoring."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class Escalation(str, Enum):
    NORMAL="normal"
    WATCH="watch"
    ELEVATED="elevated"
    CRITICAL="critical"
    ABSTAIN="abstain"

@dataclass(frozen=True, slots=True)
class EscalationAssessment:
    state: Escalation
    score: float
    triggers: tuple[str,...]
    required_action: str

class RiskEscalationEngine:
    def assess(self, *, transition_risk: float, observability: float, calibration: float, contradictions: int=0) -> EscalationAssessment:
        if min(transition_risk, observability, calibration) < 0 or max(transition_risk, observability, calibration) > 1:
            raise ValueError("risk inputs must be in [0,1]")
        if observability < .4 or calibration < .4:
            return EscalationAssessment(Escalation.ABSTAIN,0.0,("insufficient observability or calibration",),"human review")
        score=min(1.0,max(0.0,transition_risk + min(0.2,contradictions*.05)))
        state=Escalation.CRITICAL if score>=.85 else Escalation.ELEVATED if score>=.65 else Escalation.WATCH if score>=.4 else Escalation.NORMAL
        return EscalationAssessment(state,score,tuple((["transition risk"] if transition_risk>=.4 else []) + (["contradictory evidence"] if contradictions else [])),"intervene" if state is Escalation.CRITICAL else "monitor")
