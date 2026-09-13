"""Operational decision-runtime boundary linking prediction, VoI and escalation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionOption, DecisionRecommendation, DecisionSystem
from app.core.decision.value_of_information import ValueOfInformationEngine
from .risk_escalation import EscalationAssessment

@dataclass(frozen=True, slots=True)
class DecisionRuntimeResult:
    recommendation: DecisionRecommendation
    escalation: EscalationAssessment
    information_net_values: Mapping[str,float]

class DecisionRuntime:
    def __init__(self, decision_system: DecisionSystem|None=None, voi: ValueOfInformationEngine|None=None):
        self.decisions=decision_system or DecisionSystem()
        self.voi=voi or ValueOfInformationEngine()
    def decide(self, context: DecisionContext, options: Sequence[DecisionOption], escalation: EscalationAssessment, *, mode: DecisionMode=DecisionMode.ROBUST, provenance: Sequence[str]=()) -> DecisionRuntimeResult:
        if escalation.state.value in {"abstain","critical"}:
            recommendation=self.decisions._abstain(context,mode,f"escalation gate: {escalation.state.value}",provenance,("reevaluate after new evidence",))
        else:
            recommendation=self.decisions.recommend(context,options,mode=mode,provenance=provenance)
        return DecisionRuntimeResult(recommendation,escalation,{})
