"""Operational decision-runtime boundary linking prediction, VoI and escalation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence

from app.core.decision.control_plane import (
    DecisionControlPlane,
    DecisionDisposition as ControlDisposition,
    DecisionManifest,
    UncertaintyState,
)
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
    def __init__(self, decision_system: DecisionSystem | None = None,
                 voi: ValueOfInformationEngine | None = None,
                 decision_engine: DecisionEngine | None = None,
                 control_plane: DecisionControlPlane | None = None):
        self.decisions = decision_system or DecisionSystem()
        self.voi = voi or ValueOfInformationEngine()
        self.engine = decision_engine or DecisionEngine()
        self.control = control_plane or DecisionControlPlane()

    @staticmethod
    def _manifest(decision_id: str, provenance: Sequence[str],
                  assumptions: Sequence[str], scenario_refs: Sequence[str]) -> DecisionManifest:
        buckets: dict[str, list[str]] = {"state": [], "evidence": [], "model": [],
                                         "hypothesis": [], "transformation": [],
                                         "scenario": [], "constraint": []}
        for ref in provenance:
            kind, sep, value = ref.partition(":")
            key = {"state": "state", "evidence": "evidence", "model": "model",
                   "hypothesis": "hypothesis", "transform": "transformation",
                   "transformation": "transformation", "constraint": "constraint",
                   "scenario": "scenario"}.get(kind.lower() if sep else "", "evidence")
            buckets[key].append(value if sep else ref)
        buckets["scenario"].extend(scenario_refs)
        configuration_hash = sha256(("|".join(sorted(provenance)) + "|" +
                                     "|".join(sorted(assumptions))).encode()).hexdigest()
        return DecisionManifest(
            decision_id=decision_id,
            state_refs=tuple(buckets["state"] or (f"decision-state:{decision_id}",)),
            evidence_refs=tuple(buckets["evidence"]),
            model_refs=tuple(buckets["model"] or ("declared-decision-model",)),
            hypothesis_refs=tuple(buckets["hypothesis"]),
            transformation_refs=tuple(buckets["transformation"]),
            assumption_refs=tuple(assumptions),
            scenario_refs=tuple(buckets["scenario"]),
            utility_definition_ref="decision-utility:v1",
            constraint_refs=tuple(buckets["constraint"]),
            policy_version="1.0",
            configuration_hash=configuration_hash,
            code_revision="runtime-control-plane-v1",
            created_at="runtime",
        )

    def decide(self, context: DecisionContext, options: Sequence[DecisionOption],
               escalation: EscalationAssessment, *, mode: DecisionMode = DecisionMode.ROBUST,
               provenance: Sequence[str] = ()) -> DecisionRuntimeResult:
        if escalation.state.value in {"abstain", "critical"}:
            recommendation = self.decisions._abstain(
                context, mode, f"escalation gate: {escalation.state.value}",
                provenance, ("reevaluate after new evidence",),
            )
        else:
            recommendation = self.decisions.recommend(context, options, mode=mode, provenance=provenance)
        return DecisionRuntimeResult(recommendation, escalation, {})

    def decide_scenarios(self, *, decision_id: str, options: Sequence[ActionAlternative],
                         escalation: EscalationAssessment, observable: bool, identifiable: bool,
                         calibrated: bool, model_valid: bool, causal_identified: bool = True,
                         assumptions_satisfied: bool = True, mode: DecisionMode = DecisionMode.ROBUST,
                         max_harm: float | None = None, assumptions: Sequence[str] = (),
                         provenance: Sequence[str] = (), reevaluation_triggers: Sequence[str] = (),
                         purpose: str = "decision", restricted: bool = False) -> DecisionCycleResult:
        if not options or escalation.state.value in {"abstain", "critical"}:
            gate = EpistemicGate(False, False, calibrated, model_valid, causal_identified, assumptions_satisfied)
        else:
            gate = EpistemicGate(observable, identifiable, calibrated, model_valid,
                                 causal_identified, assumptions_satisfied)

        scenario_refs = tuple(f"scenario:{s.scenario_id}" for o in options for s in o.scenarios)
        manifest = self._manifest(decision_id, provenance, assumptions, scenario_refs)
        uncertainty = UncertaintyState(max((o.uncertainty for o in options), default=1.0),
                                       source_refs=tuple(provenance), method="max-option-uncertainty")
        control = self.control.authorize(decision_id=decision_id, purpose=purpose,
                                         uncertainty=uncertainty, restricted=restricted, manifest=manifest)
        if control.disposition in {ControlDisposition.ABSTAIN, ControlDisposition.HUMAN_REVIEW}:
            return self.engine.evaluate(
                decision_id=decision_id, options=options,
                gate=EpistemicGate(False, False, calibrated, model_valid,
                                   causal_identified, assumptions_satisfied),
                mode=mode, max_harm=max_harm,
                assumptions=(*assumptions, control.reason),
                provenance=(*provenance, f"audit:{control.audit_event_id}"),
                reevaluation_triggers=reevaluation_triggers,
            )
        return self.engine.evaluate(
            decision_id=decision_id, options=options, gate=gate, mode=mode,
            max_harm=max_harm, assumptions=assumptions,
            provenance=(*provenance, f"audit:{control.audit_event_id}"),
            reevaluation_triggers=reevaluation_triggers,
        )
