"""Operational decision-runtime boundary linking prediction, VoI and escalation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Mapping, Sequence

from app.core.decision.control_plane import DecisionControlPlane, DecisionDisposition as ControlDisposition, DecisionManifest, UncertaintyState
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionOption, DecisionRecommendation, DecisionSystem
from app.core.decision.engine import ActionAlternative, DecisionAudit, DecisionCycleResult, DecisionEngine, EpistemicGate
from app.core.decision.optimization import ValueOfInformation as DecisionValueOfInformation
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
        control_plane: DecisionControlPlane | None = None,
        *,
        code_revision: str = "unknown",
    ):
        if not code_revision.strip():
            raise ValueError("code_revision must not be empty")
        self.decisions = decision_system or DecisionSystem()
        self.voi = voi or ValueOfInformationEngine()
        self.engine = decision_engine or DecisionEngine()
        self.control = control_plane or DecisionControlPlane()
        self.code_revision = code_revision

    def _manifest(self, decision_id: str, provenance: Sequence[str], assumptions: Sequence[str], scenario_refs: Sequence[str]) -> DecisionManifest:
        buckets: dict[str, list[str]] = {
            "state": [], "evidence": [], "model": [], "hypothesis": [],
            "transformation": [], "scenario": [], "constraint": [],
        }
        for ref in provenance:
            kind, sep, value = ref.partition(":")
            key = {
                "state": "state", "evidence": "evidence", "model": "model",
                "hypothesis": "hypothesis", "transform": "transformation",
                "transformation": "transformation", "constraint": "constraint",
                "scenario": "scenario",
            }.get(kind.lower() if sep else "", "evidence")
            buckets[key].append(value if sep else ref)
        buckets["scenario"].extend(scenario_refs)
        raw_config = "|".join(sorted(provenance)) + "|" + "|".join(sorted(assumptions))
        return DecisionManifest(
            decision_id=decision_id,
            state_refs=tuple(buckets["state"]),
            evidence_refs=tuple(buckets["evidence"]),
            model_refs=tuple(buckets["model"]),
            hypothesis_refs=tuple(buckets["hypothesis"]),
            transformation_refs=tuple(buckets["transformation"]),
            assumption_refs=tuple(assumptions),
            scenario_refs=tuple(buckets["scenario"]),
            utility_definition_ref="decision-utility:v1",
            constraint_refs=tuple(buckets["constraint"]),
            policy_version="1.0",
            configuration_hash=sha256(raw_config.encode("utf-8")).hexdigest(),
            code_revision=self.code_revision,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def decide(
        self,
        context: DecisionContext,
        options: Sequence[DecisionOption],
        escalation: EscalationAssessment,
        *,
        mode: DecisionMode = DecisionMode.ROBUST,
        provenance: Sequence[str] = (),
        purpose: str = "decision",
        restricted: bool = False,
        information_requests: Sequence = (),
    ) -> DecisionRuntimeResult:
        triggers = ("reevaluate after new evidence", "material state change", "model validity change")
        scenario_refs = tuple(f"scenario:{scenario.scenario_id}" for option in options for scenario in option.outcomes)
        manifest = self._manifest(context.decision_id, provenance, context.assumptions, scenario_refs)
        uncertainty = UncertaintyState(max((option.uncertainty for option in options), default=1.0), source_refs=tuple(provenance), method="max-option-uncertainty")
        control = self.control.authorize(decision_id=context.decision_id, purpose=purpose, uncertainty=uncertainty, restricted=restricted, manifest=manifest)
        audit_provenance = (*provenance, f"audit:{control.audit_event_id}")
        if escalation.state.value in {"abstain", "critical"} or control.disposition is ControlDisposition.ABSTAIN:
            reason = f"escalation gate: {escalation.state.value}" if escalation.state.value in {"abstain", "critical"} else control.reason
            recommendation = self.decisions._abstain(context, mode, reason, audit_provenance, triggers)
        elif control.disposition is ControlDisposition.HUMAN_REVIEW:
            recommendation = self.decisions._abstain(context, mode, "human review required before execution", audit_provenance, triggers)
        else:
            recommendation = self.decisions.recommend(context, options, mode=mode, provenance=audit_provenance, reevaluation_triggers=triggers, information_requests=information_requests)
        return DecisionRuntimeResult(recommendation, escalation, {request.question: request.net_value for request in information_requests}, None)

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
        information_request: DecisionValueOfInformation | None = None,
        assumptions: Sequence[str] = (),
        provenance: Sequence[str] = (),
        reevaluation_triggers: Sequence[str] = (),
        purpose: str = "decision",
        restricted: bool = False,
    ) -> DecisionCycleResult:
        gate = (
            EpistemicGate(False, False, calibrated, model_valid, causal_identified, assumptions_satisfied)
            if not options or escalation.state.value in {"abstain", "critical"}
            else EpistemicGate(observable, identifiable, calibrated, model_valid, causal_identified, assumptions_satisfied)
        )
        scenario_refs = tuple(f"scenario:{s.scenario_id}" for o in options for s in o.scenarios)
        manifest = self._manifest(decision_id, provenance, assumptions, scenario_refs)
        uncertainty = UncertaintyState(max((o.uncertainty for o in options), default=1.0), source_refs=tuple(provenance), method="max-option-uncertainty")
        control = self.control.authorize(decision_id=decision_id, purpose=purpose, uncertainty=uncertainty, restricted=restricted, manifest=manifest)
        if control.disposition in {ControlDisposition.ABSTAIN, ControlDisposition.HUMAN_REVIEW}:
            gate = EpistemicGate(False, False, calibrated, model_valid, causal_identified, assumptions_satisfied)
        control_assumption = ("human review required before execution",) if control.disposition is ControlDisposition.HUMAN_REVIEW else ()
        return self.engine.evaluate(
            decision_id=decision_id,
            options=options,
            gate=gate,
            mode=mode,
            max_harm=max_harm,
            information_request=information_request,
            assumptions=(*assumptions, *control_assumption),
            provenance=(*provenance, f"audit:{control.audit_event_id}"),
            reevaluation_triggers=reevaluation_triggers,
        )
