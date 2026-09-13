"""Canonical executable CeutIA decision loop.

The loop is the integration point for evidence/state, epistemic gates,
scenario alternatives, value of information, governance and audit.  It does
not replace specialist engines; it enforces their ordering and contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .control_plane import (
    DecisionControlPlane,
    DecisionDisposition as ControlDisposition,
    DecisionManifest,
    UncertaintyState,
)
from .decision_system import DecisionMode
from .engine import (
    ActionAlternative,
    DecisionAction,
    DecisionAudit,
    DecisionCycleResult,
    DecisionEngine,
    EpistemicGate,
)
from .optimization import ValueOfInformation


@dataclass(frozen=True, slots=True)
class DecisionLoopInput:
    decision_id: str
    options: tuple[ActionAlternative, ...]
    gate: EpistemicGate
    uncertainty: UncertaintyState
    provenance: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    reevaluation_triggers: tuple[str, ...] = ()
    information_request: ValueOfInformation | None = None
    purpose: str = "decision"
    restricted: bool = False
    mode: DecisionMode = DecisionMode.ROBUST
    max_harm: float | None = None


class DecisionLoop:
    def __init__(self, engine: DecisionEngine | None = None,
                 control: DecisionControlPlane | None = None) -> None:
        self.engine = engine or DecisionEngine()
        self.control = control or DecisionControlPlane()

    @staticmethod
    def _manifest(item: DecisionLoopInput) -> DecisionManifest:
        buckets = {"state": [], "evidence": [], "model": [], "hypothesis": [],
                   "transformation": [], "constraint": []}
        for ref in item.provenance:
            kind, sep, value = ref.partition(":")
            key = {"state": "state", "evidence": "evidence", "model": "model",
                   "hypothesis": "hypothesis", "transform": "transformation",
                   "transformation": "transformation", "constraint": "constraint"}.get(
                       kind.lower() if sep else "", "evidence")
            buckets[key].append(value if sep else ref)
        scenarios = tuple(f"scenario:{s.scenario_id}" for o in item.options for s in o.scenarios)
        raw_configuration = "|".join(sorted((*item.provenance, *item.assumptions)))
        configuration_hash = sha256(raw_configuration.encode("utf-8")).hexdigest()
        return DecisionManifest(
            decision_id=item.decision_id,
            state_refs=tuple(buckets["state"] or (f"decision-state:{item.decision_id}",)),
            evidence_refs=tuple(buckets["evidence"]),
            model_refs=tuple(buckets["model"]),
            hypothesis_refs=tuple(buckets["hypothesis"]),
            transformation_refs=tuple(buckets["transformation"]),
            assumption_refs=item.assumptions,
            scenario_refs=scenarios,
            utility_definition_ref="decision-utility:v1",
            constraint_refs=tuple(buckets["constraint"]),
            policy_version="1.0",
            configuration_hash=configuration_hash,
            code_revision="decision-loop-v1",
            created_at="runtime",
        )

    def run(self, item: DecisionLoopInput) -> DecisionCycleResult:
        if not item.decision_id:
            raise ValueError("decision_id is required")
        if not item.options:
            raise ValueError("at least one decision option is required")

        manifest = self._manifest(item)
        control = self.control.authorize(
            decision_id=item.decision_id,
            purpose=item.purpose,
            uncertainty=item.uncertainty,
            restricted=item.restricted,
            manifest=manifest,
        )

        if control.disposition is ControlDisposition.ABSTAIN:
            return DecisionCycleResult(
                DecisionAudit(item.decision_id, DecisionAction.ABSTAIN, "ABSTAIN", item.mode.value,
                              (control.reason,), None, None, None, None, 0.0,
                              item.assumptions, (*item.provenance, f"audit:{control.audit_event_id}"),
                              item.reevaluation_triggers),
                None, item.information_request,
            )

        if control.disposition is ControlDisposition.HUMAN_REVIEW:
            return DecisionCycleResult(
                DecisionAudit(item.decision_id, DecisionAction.HUMAN_REVIEW, "HUMAN_REVIEW", item.mode.value,
                              (control.reason,), None, None, None, None, 0.0,
                              item.assumptions, (*item.provenance, f"audit:{control.audit_event_id}"),
                              item.reevaluation_triggers),
                None, item.information_request,
            )

        return self.engine.evaluate(
            decision_id=item.decision_id,
            options=item.options,
            gate=item.gate,
            mode=item.mode,
            max_harm=item.max_harm,
            information_request=item.information_request,
            assumptions=item.assumptions,
            provenance=(*item.provenance, f"audit:{control.audit_event_id}"),
            reevaluation_triggers=item.reevaluation_triggers,
        )


__all__ = ["DecisionLoop", "DecisionLoopInput"]
