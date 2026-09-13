"""Operational decision-runtime boundary linking prediction, VoI and escalation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from app.core.decision.decision_system import (
    DecisionContext,
    DecisionMode,
    DecisionOption,
    DecisionRecommendation,
    DecisionSystem,
)
from app.core.decision.engine import (
    ActionAlternative,
    DecisionAudit,
    DecisionCycleResult,
    DecisionEngine,
    EpistemicGate,
)
from app.core.decision.value_of_information import ValueOfInformationEngine
from .risk_escalation import EscalationAssessment


@dataclass(frozen=True, slots=True)
class DecisionRuntimeResult:
    recommendation: DecisionRecommendation
    escalation: EscalationAssessment
    information_net_values: Mapping[str, float]
    decision_audit: DecisionAudit | None = None


class DecisionRuntime:
    def __init__(
        self,
        decision_system: DecisionSystem | None = None,
        voi: ValueOfInformationEngine | None = None,
        decision_engine: DecisionEngine | None = None,
    ):
        self.decisions = decision_system or DecisionSystem()
        self.voi = voi or ValueOfInformationEngine()
        self.engine = decision_engine or DecisionEngine()

    def decide(
        self,
        context: DecisionContext,
        options: Sequence[DecisionOption],
        escalation: EscalationAssessment,
        *,
        mode: DecisionMode = DecisionMode.ROBUST,
        provenance: Sequence[str] = (),
    ) -> DecisionRuntimeResult:
        if escalation.state.value in {"abstain", "critical"}:
            recommendation = self.decisions._abstain(
                context, mode, f"escalation gate: {escalation.state.value}",
                provenance, ("reevaluate after new evidence",),
            )
        else:
            recommendation = self.decisions.recommend(
                context, options, mode=mode, provenance=provenance,
            )
        return DecisionRuntimeResult(recommendation, escalation, {})

    def decide_scenarios(
        self,
        *,
        decision_id: str,
        options: Sequence[ActionAlternative],
        escalation: EscalationAssessment,
        observable: bool,
        identifiable: bool,
        calibrated: bool,
        model_valid: bool,
        causal_identified: bool = True,
        assumptions_satisfied: bool = True,
        mode: DecisionMode = DecisionMode.ROBUST,
        max_harm: float | None = None,
        assumptions: Sequence[str] = (),
        provenance: Sequence[str] = (),
        reevaluation_triggers: Sequence[str] = (),
    ) -> DecisionCycleResult:
        """Execute the stricter scenario-based decision cycle.

        Escalation is an independent safety gate. Scientific validity is a
        separate epistemic gate; neither is silently substituted for the other.
        """
        if escalation.state.value in {"abstain", "critical"}:
            gate = EpistemicGate(False, False, calibrated, model_valid,
                                 causal_identified, assumptions_satisfied)
        else:
            gate = EpistemicGate(
                observable, identifiable, calibrated, model_valid,
                causal_identified, assumptions_satisfied,
            )
        return self.engine.evaluate(
            decision_id=decision_id,
            options=options,
            gate=gate,
            mode=mode,
            max_harm=max_harm,
            assumptions=assumptions,
            provenance=provenance,
            reevaluation_triggers=reevaluation_triggers,
        )
