"""Canonical closed-loop representation for arbitrary complex systems.

The engine turns CeutIA's previously separate scientific primitives into one
reusable lifecycle:

observations -> state -> trajectory -> dynamics -> uncertainty -> relations
-> hypotheses/causality -> prediction -> decision -> response -> learning.

This module is deliberately a kernel, not a monolithic implementation of every
scientific method. Specialist engines remain responsible for estimation,
causal identification, forecasting, network analysis and decision mathematics.
The kernel owns identity, temporal ordering, provenance, epistemic boundaries,
state continuity and closed-loop orchestration.

No stage silently upgrades epistemic status. A forecast is not causal evidence;
a state estimate is not an observation; a recommendation is not an intervention;
and an intervention outcome is not automatically a causal effect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable, Mapping, Sequence

from ..decision.decision_system import (
    DecisionContext,
    DecisionMode,
    DecisionOption,
    DecisionRecommendation,
    DecisionSystem,
)
from ..errors import ContractViolation, TemporalViolation
from ..inference.inference_engine import (
    EvidenceContribution,
    EpistemicLevel,
    InferencePlan,
    InferenceProblem,
    InferenceResult,
    ScientificInferenceEngine,
)
from ..integration.system_context import SystemContext
from ..pipeline.contracts import ObservationRecord


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
    """Auditable statement about one lifecycle stage."""

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
    """Runtime input required to advance the integrated kernel."""

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

    def __post_init__(self) -> None:
        if self.context.as_of.tzinfo is None or self.context.as_of.utcoffset() is None:
            raise TemporalViolation("context timestamp must be timezone-aware")
        if self.decision_options and self.decision_context is None:
            raise ContractViolation("decision options require a decision context")


@dataclass(frozen=True, slots=True)
class ClosedLoopSnapshot:
    """Complete machine-readable view of one closed-loop inference cycle."""

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
    """Canonical reusable representation of one evolving complex system.

    The kernel is intentionally domain-neutral. Domain-specific semantics enter
    through typed context records and specialist engines rather than through a
    hard-coded ontology.
    """

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
    """Orchestrates the full observation-to-learning cycle in real time.

    Real-time here means deterministic, bounded orchestration at event arrival;
    it does not imply that every scientific method is computationally real-time.
    Expensive specialist inference may remain asynchronous while the kernel
    preserves the same causal/epistemic lifecycle and provenance.
    """

    _STAGE_ORDER = (
        Stage.OBSERVATION,
        Stage.STATE,
        Stage.TRAJECTORY,
        Stage.DYNAMICS,
        Stage.UNCERTAINTY,
        Stage.RELATIONS,
        Stage.HYPOTHESES,
        Stage.CAUSALITY,
        Stage.PREDICTION,
        Stage.DECISION,
        Stage.RESPONSE,
        Stage.LEARNING,
    )

    def __init__(
        self,
        *,
        inference_engine: ScientificInferenceEngine | None = None,
        decision_system: DecisionSystem | None = None,
    ) -> None:
        self.inference_engine = inference_engine or ScientificInferenceEngine()
        self.decision_system = decision_system or DecisionSystem()

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

        stages = self._build_stage_records(event, inference.plan)
        decision: DecisionRecommendation | None = None
        if event.decision_context is not None:
            if not inference.usable:
                decision = self.decision_system._abstain(
                    event.decision_context,
                    event.decision_mode,
                    "inference is not decision-ready",
                    context.current_state.evidence_ids,
                    ("new evidence", "state update", "model validity change"),
                )
            else:
                decision = self.decision_system.recommend(
                    event.decision_context,
                    event.decision_options,
                    mode=event.decision_mode,
                    provenance=tuple(context.current_state.evidence_ids),
                    reevaluation_triggers=("new observation", "material state change", "model validity change"),
                )

        lineage = self._lineage(event, inference, decision)
        snapshot = ClosedLoopSnapshot(
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
            lineage=lineage,
        )
        return snapshot

    def _build_stage_records(self, event: ClosedLoopInput, plan: InferencePlan) -> tuple[StageRecord, ...]:
        context = event.context
        observation_ids = tuple(item.observation_id for item in context.observations)
        state_id = context.state.state.state_id
        trajectory_ids = tuple(item.state.state_id for item in context.trajectory.snapshots)
        dynamics_ids = tuple(
            f"transition:{item.from_state_id}->{item.to_state_id}"
            for item in context.trajectory.transitions()
        )
        uncertainty_ids = tuple(item.model_id for item in context.models)
        records = (
            StageRecord(Stage.OBSERVATION, observation_ids, EpistemicLevel.OBSERVED, context.as_of),
            StageRecord(Stage.STATE, (state_id,), EpistemicLevel.ESTIMATED, context.as_of, (Stage.OBSERVATION,)),
            StageRecord(Stage.TRAJECTORY, trajectory_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.STATE,)),
            StageRecord(Stage.DYNAMICS, dynamics_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.TRAJECTORY,)),
            StageRecord(Stage.UNCERTAINTY, uncertainty_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.STATE, Stage.DYNAMICS), (event.uncertainty_summary,)),
            StageRecord(Stage.RELATIONS, event.relation_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.STATE, Stage.TRAJECTORY)),
            StageRecord(Stage.HYPOTHESES, event.hypothesis_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.OBSERVATION, Stage.RELATIONS)),
            StageRecord(Stage.CAUSALITY, event.causal_model_ids, EpistemicLevel.CAUSAL if event.causal_model_ids else EpistemicLevel.ESTIMATED, context.as_of, (Stage.HYPOTHESES,)),
            StageRecord(Stage.PREDICTION, event.prediction_ids, EpistemicLevel.PREDICTIVE, context.as_of, (Stage.STATE, Stage.DYNAMICS, Stage.UNCERTAINTY), plan.warnings),
            StageRecord(Stage.DECISION, (event.decision_context.decision_id,) if event.decision_context else (), EpistemicLevel.DECISIONAL, context.as_of, (Stage.PREDICTION, Stage.UNCERTAINTY)),
            StageRecord(Stage.RESPONSE, event.response_ids, EpistemicLevel.OBSERVED, context.as_of, (Stage.DECISION,)),
            StageRecord(Stage.LEARNING, event.learning_ids, EpistemicLevel.ESTIMATED, context.as_of, (Stage.RESPONSE,)),
        )
        return records

    @staticmethod
    def _lineage(
        event: ClosedLoopInput,
        inference: InferenceResult,
        decision: DecisionRecommendation | None,
    ) -> tuple[str, ...]:
        context = event.context
        ids: list[str] = [
            f"system:{context.system_id}",
            f"state:{context.state.state.state_id}",
            *sorted(f"observation:{item.observation_id}" for item in context.observations),
            *sorted(f"evidence:{item.evidence_id}" for item in context.evidence),
        ]
        ids.extend(f"model:{item.model_id}" for item in context.models)
        ids.extend(f"hypothesis:{item}" for item in event.hypothesis_ids)
        ids.extend(f"causal:{item}" for item in event.causal_model_ids)
        ids.extend(f"prediction:{item}" for item in event.prediction_ids)
        if decision is not None:
            ids.append(f"decision:{decision.decision_id}")
            ids.append(f"option:{decision.option_id}")
        ids.extend(f"response:{item}" for item in event.response_ids)
        ids.extend(f"learning:{item}" for item in event.learning_ids)
        ids.append(f"inference-regime:{inference.plan.primary.value}")
        return tuple(dict.fromkeys(ids))


__all__ = [
    "ClosedLoopEngine",
    "ClosedLoopInput",
    "ClosedLoopSnapshot",
    "Stage",
    "StageRecord",
    "SystemKernel",
]
