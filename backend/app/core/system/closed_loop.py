"""Canonical closed-loop representation for arbitrary complex systems.

observations -> state -> trajectory -> dynamics -> uncertainty -> relations
-> hypotheses/causality -> prediction -> decision -> response -> learning.

The kernel owns identity, temporal ordering, provenance, epistemic boundaries,
state continuity and orchestration. Specialist scientific engines retain
responsibility for estimation, causal identification, forecasting, network
analysis and decision mathematics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from hashlib import sha256

from ..decision.control_plane import (
    DecisionControlPlane,
    DecisionDisposition as ControlDisposition,
    DecisionManifest,
    UncertaintyState,
)
from ..decision.decision_system import (
    DecisionContext, DecisionMode, DecisionOption, DecisionRecommendation, DecisionSystem,
)
from ..errors import ContractViolation, TemporalViolation
from ..inference.inference_engine import (
    EvidenceContribution, EpistemicLevel, InferencePlan, InferenceProblem,
    InferenceResult, ScientificInferenceEngine,
)
from ..integration.system_context import SystemContext


class Stage(str, Enum):
    OBSERVATION = "observation"
    STATE = "state"
    TRAJECTORY = "trajectory"
    DYNAMICS = "dynamics"
    UNCERTAINTY = "uncertainty"
    RELATIONS = "relations"
    HYPOTHESES = "hypotheses"
    CAUSALITY = "causality"
    PREDICTION = "prediction"
    DECISION = "decision"
    RESPONSE = "response"
    LEARNING = "learning"


@dataclass(frozen=True, slots=True)
class StageRecord:
    stage: Stage
    record_ids: tuple[str, ...]
    epistemic_level: EpistemicLevel
    as_of: datetime
    depends_on: tuple[Stage, ...] = ()
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise TemporalViolation("stage timestamp must be timezone-aware")
        if any(not item for item in self.record_ids):
            raise ContractViolation("stage record IDs cannot be empty")


@dataclass(frozen=True, slots=True)
class ClosedLoopInput:
    context: SystemContext
    inference_problem: InferenceProblem
    decision_context: DecisionContext | None = None
    decision_options: tuple[DecisionOption, ...] = ()
    decision_mode: DecisionMode = DecisionMode.ROBUST
    evidence: tuple[EvidenceContribution, ...] = ()
    prediction_ids: tuple[str, ...] = ()
    relation_ids: tuple[str, ...] = ()
    hypothesis_ids: tuple[str, ...] = ()
    causal_model_ids: tuple[str, ...] = ()
    response_ids: tuple[str, ...] = ()
    learning_ids: tuple[str, ...] = ()
    uncertainty_summary: str = "uncertainty not yet quantified"
    claims: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    purpose: str = "closed-loop decision"
    restricted: bool = False

    def __post_init__(self) -> None:
        if self.context.as_of.tzinfo is None or self.context.as_of.utcoffset() is None:
            raise TemporalViolation("context timestamp must be timezone-aware")
        if self.decision_options and self.decision_context is None:
            raise ContractViolation("decision options require a decision context")


@dataclass(frozen=True, slots=True)
class ClosedLoopSnapshot:
    system_id: str
    as_of: datetime
    context: SystemContext
    stages: tuple[StageRecord, ...]
    inference: InferenceResult
    decision: DecisionRecommendation | None
    prediction_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]
    hypothesis_ids: tuple[str, ...]
    causal_model_ids: tuple[str, ...]
    response_ids: tuple[str, ...]
    learning_ids: tuple[str, ...]
    lineage: tuple[str, ...]

    @property
    def decision_ready(self) -> bool:
        return self.inference.usable and self.decision is not None

    @property
    def closed_loop_complete(self) -> bool:
        return bool(self.response_ids and self.learning_ids)

    @property
    def epistemic_chain(self) -> tuple[str, ...]:
        return tuple(stage.epistemic_level.value for stage in self.stages)


@dataclass(slots=True)
class SystemKernel:
    """Append-only temporal memory of the complete system lifecycle."""

    system_id: str
    snapshots: list[ClosedLoopSnapshot] = field(default_factory=list)

    def append(self, snapshot: ClosedLoopSnapshot) -> None:
        if snapshot.system_id != self.system_id:
            raise ContractViolation("snapshot system_id does not match kernel")
        if self.snapshots and snapshot.as_of <= self.snapshots[-1].as_of:
            raise TemporalViolation("kernel cycles must advance strictly in time")
        self.snapshots.append(snapshot)

    @property
    def latest(self) -> ClosedLoopSnapshot | None:
        return self.snapshots[-1] if self.snapshots else None

    def history(self) -> tuple[ClosedLoopSnapshot, ...]:
        return tuple(self.snapshots)

    def stage_history(self, stage: Stage) -> tuple[StageRecord, ...]:
        return tuple(record for snapshot in self.snapshots for record in snapshot.stages if record.stage is stage)


class ClosedLoopEngine:
    """Bounded real-time orchestration over the complete scientific lifecycle."""

    def __init__(self, *, inference_engine: ScientificInferenceEngine | None = None,
                 decision_system: DecisionSystem | None = None,
                 control_plane: DecisionControlPlane | None = None) -> None:
        self.inference_engine = inference_engine or ScientificInferenceEngine()
        self.decision_system = decision_system or DecisionSystem()
        self.control_plane = control_plane or DecisionControlPlane()

    @staticmethod
    def _decision_manifest(event: ClosedLoopInput) -> DecisionManifest:
        context = event.context
        state_refs = (f"state:{context.state.state.state_id}",)
        evidence_refs = tuple(dict.fromkeys(
            [f"evidence:{x.evidence_id}" for x in context.evidence]
            + [f"evidence:{x.evidence_id}" for x in event.evidence]
        ))
        model_refs = tuple(f"model:{x.model_id}" for x in context.models)
        hypothesis_refs = tuple(f"hypothesis:{x}" for x in event.hypothesis_ids)
        scenario_refs = tuple(
            f"scenario:{scenario.scenario_id}"
            for option in event.decision_options
            for scenario in option.outcomes
        )
        constraint_refs = tuple(f"constraint:{key}" for key in event.decision_context.constraints) if event.decision_context else ()
        assumptions = event.decision_context.assumptions if event.decision_context else ()
        raw_config = "|".join(sorted((
            *state_refs, *evidence_refs, *model_refs, *hypothesis_refs,
            *scenario_refs, *constraint_refs, *assumptions,
        )))
        configuration_hash = sha256(raw_config.encode("utf-8")).hexdigest()
        return DecisionManifest(
            decision_id=event.decision_context.decision_id if event.decision_context else "",
            state_refs=state_refs,
            evidence_refs=evidence_refs,
            model_refs=model_refs,
            hypothesis_refs=hypothesis_refs,
            transformation_refs=(),
            assumption_refs=assumptions,
            scenario_refs=scenario_refs,
            utility_definition_ref="decision-objectives:v1",
            constraint_refs=constraint_refs,
            policy_version="1.0",
            configuration_hash=configuration_hash,
            code_revision="closed-loop-v1",
            created_at=event.context.as_of.isoformat(),
        )

    def process(self, event: ClosedLoopInput) -> ClosedLoopSnapshot:
        context = event.context
        inference = self.inference_engine.compose(
            event.inference_problem,
            evidence=event.evidence,
            epistemic_level=EpistemicLevel.ESTIMATED,
            claims=event.claims,
            uncertainty_summary=event.uncertainty_summary,
            limitations=event.limitations,
        )
        decision: DecisionRecommendation | None = None
        audit_id: str | None = None
        if event.decision_context is not None:
            provenance = tuple(dict.fromkeys(
                [f"state:{context.state.state.state_id}"]
                + [f"observation:{x.observation_id}" for x in context.observations]
                + [f"evidence:{x.evidence_id}" for x in context.evidence]
                + [f"evidence:{x.evidence_id}" for x in event.evidence]
                + [f"model:{x.model_id}" for x in context.models]
                + [f"hypothesis:{x}" for x in event.hypothesis_ids]
                + [f"causal:{x}" for x in event.causal_model_ids]
                + [f"prediction:{x}" for x in event.prediction_ids]
            ))
            triggers = ("new observation", "material state change", "model validity change", "decision validity window expired")
            if not inference.usable:
                decision = self.decision_system._abstain(
                    event.decision_context, event.decision_mode,
                    "inference is not decision-ready", provenance, triggers,
                )
            elif not event.decision_options:
                decision = self.decision_system._abstain(
                    event.decision_context, event.decision_mode,
                    "no admissible options", provenance, triggers,
                )
            else:
                uncertainty = max(option.uncertainty for option in event.decision_options)
                manifest = self._decision_manifest(event)
                control = self.control_plane.authorize(
                    decision_id=event.decision_context.decision_id,
                    purpose=event.purpose,
                    uncertainty=UncertaintyState(
                        uncertainty,
                        source_refs=tuple(dict.fromkeys((*provenance, *event.causal_model_ids))),
                        method="decision-option-conservative-max",
                    ),
                    restricted=event.restricted,
                    manifest=manifest,
                )
                audit_id = control.audit_event_id
                if control.disposition is ControlDisposition.ABSTAIN:
                    decision = self.decision_system._abstain(
                        event.decision_context, event.decision_mode,
                        control.reason, (*provenance, f"audit:{audit_id}"), triggers,
                    )
                else:
                    decision = self.decision_system.recommend(
                        event.decision_context, event.decision_options,
                        mode=event.decision_mode, provenance=(*provenance, f"audit:{audit_id}"),
                        reevaluation_triggers=triggers,
                    )
        stages = self._build_stage_records(event, inference.plan)
        return ClosedLoopSnapshot(
            system_id=context.system_id,
            as_of=context.as_of,
            context=context,
            stages=stages,
            inference=inference,
            decision=decision,
            prediction_ids=event.prediction_ids,
            relation_ids=event.relation_ids,
            hypothesis_ids=event.hypothesis_ids,
            causal_model_ids=event.causal_model_ids,
            response_ids=event.response_ids,
            learning_ids=event.learning_ids,
            lineage=self._lineage(event, inference, decision, audit_id=audit_id),
        )

    def process_into(self, kernel: SystemKernel, event: ClosedLoopInput) -> ClosedLoopSnapshot:
        """Process and atomically append the resulting cycle to system memory."""
        snapshot = self.process(event)
        kernel.append(snapshot)
        return snapshot

    def _build_stage_records(self, event: ClosedLoopInput, plan: InferencePlan) -> tuple[StageRecord, ...]:
        context = event.context
        observations = tuple(item.observation_id for item in context.observations)
        state_id = context.state.state.state_id
        trajectory = tuple(item.state.state_id for item in context.trajectory.snapshots)
        dynamics = tuple(f"transition:{x.from_state_id}->{x.to_state_id}" for x in context.trajectory.transitions())
        uncertainty = tuple(item.model_id for item in context.models)
        return (
            StageRecord(Stage.OBSERVATION, observations, EpistemicLevel.OBSERVED, context.as_of),
            StageRecord(Stage.STATE, (state_id,), EpistemicLevel.ESTIMATED, context.as_of, (Stage.OBSERVATION,)),
            StageRecord(Stage.TRAJECTORY, trajectory, EpistemicLevel.ESTIMATED, context.as_of, (Stage.STATE,)),
            StageRecord(Stage.DYNAMICS, dynamics, EpistemicLevel.ESTIMATED, context.as_of, (Stage.TRAJECTORY,)),
            StageRecord(Stage.UNCERTAINTY, uncertainty, EpistemicLevel.ESTIMATED, context.as_of,
                        (Stage.STATE, Stage.DYNAMICS), (event.uncertainty_summary,)),
            StageRecord(Stage.RELATIONS, event.relation_ids, EpistemicLevel.ESTIMATED, context.as_of,
                        (Stage.STATE, Stage.TRAJECTORY)),
            StageRecord(Stage.HYPOTHESES, event.hypothesis_ids, EpistemicLevel.ESTIMATED, context.as_of,
                        (Stage.OBSERVATION, Stage.RELATIONS)),
            StageRecord(Stage.CAUSALITY, event.causal_model_ids,
                        EpistemicLevel.CAUSAL if event.causal_model_ids else EpistemicLevel.ESTIMATED,
                        context.as_of, (Stage.HYPOTHESES,)),
            StageRecord(Stage.PREDICTION, event.prediction_ids, EpistemicLevel.PREDICTIVE, context.as_of,
                        (Stage.STATE, Stage.DYNAMICS, Stage.UNCERTAINTY), plan.warnings),
            StageRecord(Stage.DECISION, (event.decision_context.decision_id,) if event.decision_context else (),
                        EpistemicLevel.DECISIONAL, context.as_of, (Stage.PREDICTION, Stage.UNCERTAINTY)),
            StageRecord(Stage.RESPONSE, event.response_ids, EpistemicLevel.OBSERVED, context.as_of, (Stage.DECISION,)),
            StageRecord(Stage.LEARNING, event.learning_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.RESPONSE,)),
        )

    @staticmethod
    def _lineage(event: ClosedLoopInput, inference: InferenceResult,
                 decision: DecisionRecommendation | None, *, audit_id: str | None = None) -> tuple[str, ...]:
        context = event.context
        ids = [f"system:{context.system_id}", f"state:{context.state.state.state_id}"]
        ids.extend(sorted(f"observation:{x.observation_id}" for x in context.observations))
        ids.extend(sorted(f"evidence:{x.evidence_id}" for x in context.evidence))
        ids.extend(f"model:{x.model_id}" for x in context.models)
        ids.extend(f"hypothesis:{x}" for x in event.hypothesis_ids)
        ids.extend(f"causal:{x}" for x in event.causal_model_ids)
        ids.extend(f"prediction:{x}" for x in event.prediction_ids)
        if decision is not None:
            ids.extend((f"decision:{decision.decision_id}", f"option:{decision.option_id}"))
        if audit_id is not None:
            ids.append(f"audit:{audit_id}")
        ids.extend(f"response:{x}" for x in event.response_ids)
        ids.extend(f"learning:{x}" for x in event.learning_ids)
        ids.append(f"inference-regime:{inference.plan.primary.value}")
        return tuple(dict.fromkeys(ids))


__all__ = ["ClosedLoopEngine", "ClosedLoopInput", "ClosedLoopSnapshot", "Stage", "StageRecord", "SystemKernel"]
