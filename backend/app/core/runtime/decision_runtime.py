"""Operational decision-runtime boundary linking prediction, VoI and escalation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Mapping, Sequence

from app.core.decision.control_plane import DecisionControlPlane, DecisionDisposition as ControlDisposition, DecisionManifest, UncertaintyState
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionOption, DecisionRecommendation, DecisionSystem, InformationRequest
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
    control_audit_event_id: str | None = None


class DecisionRuntime:
    def __init__(self, decision_system: DecisionSystem | None = None, voi: ValueOfInformationEngine | None = None, decision_engine: DecisionEngine | None = None, control_plane: DecisionControlPlane | None = None, *, code_revision: str = "unknown"):
        if not code_revision.strip() or code_revision.strip().lower() in {"unknown", "unresolved", "dirty"}:
            raise ValueError("code_revision must identify an exact reproducible revision")
        self.decisions = decision_system or DecisionSystem()
        self.voi = voi or ValueOfInformationEngine()
        self.engine = decision_engine or DecisionEngine()
        self.control = control_plane or DecisionControlPlane()
        self.code_revision = code_revision

    def _manifest(self, decision_id: str, provenance: Sequence[str], assumptions: Sequence[str], scenario_refs: Sequence[str]) -> DecisionManifest:
        buckets: dict[str, list[str]] = {"state": [], "evidence": [], "model": [], "hypothesis": [], "transformation": [], "scenario": [], "constraint": []}
        for ref in provenance:
            kind, sep, value = ref.partition(":")
            key = {"state": "state", "evidence": "evidence", "model": "model", "hypothesis": "hypothesis", "transform": "transformation", "transformation": "transformation", "constraint": "constraint", "scenario": "scenario"}.get(kind.lower() if sep else "", "evidence")
            buckets[key].append(value if sep else ref)
        buckets["scenario"].extend(scenario_refs)
        raw_config = "|".join(sorted(provenance)) + "|" + "|".join(sorted(assumptions))
        return DecisionManifest(decision_id, tuple(buckets["state"]), tuple(buckets["evidence"]), tuple(buckets["model"]), tuple(buckets["hypothesis"]), tuple(buckets["transformation"]), tuple(assumptions), tuple(buckets["scenario"]), "decision-utility:v1", tuple(buckets["constraint"]), "1.0", sha256(raw_config.encode("utf-8")).hexdigest(), self.code_revision, datetime.now(timezone.utc).isoformat())

    def decide(self, context: DecisionContext, options: Sequence[DecisionOption], escalation: EscalationAssessment, *, mode: DecisionMode = DecisionMode.ROBUST, provenance: Sequence[str] = (), purpose: str = "decision", restricted: bool = False, information_requests: Sequence[InformationRequest] = (), at: datetime | None = None, epistemic_uncertainty: float | None = None, epistemic_refs: Sequence[str] = ()) -> DecisionRuntimeResult:
        """Authorize a decision using both model uncertainty and evidence-derived epistemic uncertainty.

        ``epistemic_uncertainty`` must come from an evidence/estimation layer such as
        ``EvidenceDecisionBridge``. It is never inferred from the client-facing text.
        The control plane combines it conservatively with option uncertainty.
        """
        if epistemic_uncertainty is not None and not 0.0 <= epistemic_uncertainty <= 1.0:
            raise ValueError("epistemic_uncertainty must be in [0,1]")
        triggers = ("reevaluate after new evidence", "material state change", "model validity change")
        scenario_refs = tuple(f"scenario:{scenario.scenario_id}" for option in options for scenario in option.outcomes)
        manifest = self._manifest(context.decision_id, (*provenance, *epistemic_refs), context.assumptions, scenario_refs)
        option_uncertainty = max((option.uncertainty for option in options), default=1.0)
        combined_uncertainty = max(option_uncertainty, epistemic_uncertainty or 0.0)
        uncertainty = UncertaintyState(combined_uncertainty, source_refs=tuple((*provenance, *epistemic_refs)), method="conservative-max-model-and-epistemic")
        control = self.control.authorize(decision_id=context.decision_id, purpose=purpose, uncertainty=uncertainty, restricted=restricted, manifest=manifest)
        audit_provenance = (*provenance, *epistemic_refs, f"audit:{control.audit_event_id}")
        if escalation.state.value in {"abstain", "critical"} or control.disposition is ControlDisposition.ABSTAIN:
            reason = f"escalation gate: {escalation.state.value}" if escalation.state.value in {"abstain", "critical"} else control.reason
            recommendation = self.decisions._abstain(context, mode, reason, audit_provenance, triggers)
        elif control.disposition is ControlDisposition.HUMAN_REVIEW:
            recommendation = self.decisions._abstain(context, mode, "human review required before execution", audit_provenance, triggers)
        else:
            recommendation = self.decisions.recommend(context, options, mode=mode, provenance=audit_provenance, reevaluation_triggers=triggers, information_requests=information_requests, at=at)
        return DecisionRuntimeResult(recommendation, escalation, {request.question: request.net_value for request in information_requests}, None, control.audit_event_id)

    def decide_scenarios(self, *, decision_id: str, options: Sequence[ActionAlternative], escalation: EscalationAssessment, observable: bool, identifiable: bool, calibrated: bool, model_valid: bool, causal_identified: bool = True, assumptions_satisfied: bool = True, mode: DecisionMode = DecisionMode.ROBUST, max_harm: float | None = None, information_request: DecisionValueOfInformation | None = None, assumptions: Sequence[str] = (), provenance: Sequence[str] = (), reevaluation_triggers: Sequence[str] = (), purpose: str = "decision", restricted: bool = False) -> DecisionCycleResult:
        gate = EpistemicGate(False, False, calibrated, model_valid, causal_identified, assumptions_satisfied) if not options or escalation.state.value in {"abstain", "critical"} else EpistemicGate(observable, identifiable, calibrated, model_valid, causal_identified, assumptions_satisfied)
        scenario_refs = tuple(f"scenario:{s.scenario_id}" for o in options for s in o.scenarios)
        manifest = self._manifest(decision_id, provenance, assumptions, scenario_refs)
        uncertainty = UncertaintyState(max((o.uncertainty for o in options), default=1.0), source_refs=tuple(provenance), method="max-option-uncertainty")
        control = self.control.authorize(decision_id=decision_id, purpose=purpose, uncertainty=uncertainty, restricted=restricted, manifest=manifest)
        if control.disposition in {ControlDisposition.ABSTAIN, ControlDisposition.HUMAN_REVIEW}:
            gate = EpistemicGate(False, False, calibrated, model_valid, causal_identified, assumptions_satisfied)
        control_assumption = ("human review required before execution",) if control.disposition is ControlDisposition.HUMAN_REVIEW else ()
        return self.engine.evaluate(decision_id=decision_id, options=options, gate=gate, mode=mode, max_harm=max_harm, information_request=information_request, assumptions=(*assumptions, *control_assumption), provenance=(*provenance, f"audit:{control.audit_event_id}"), reevaluation_triggers=reevaluation_triggers)
