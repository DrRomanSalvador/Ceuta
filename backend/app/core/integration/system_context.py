"""Canonical integrated context for CeutIA's dynamic-system lifecycle.

This module is deliberately an orchestration boundary, not a replacement for
specialist analytical engines. It gives every downstream layer one coherent,
provenance-aware state/trajectory context and preserves uncertainty,
contradictions and epistemic status without promoting any inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from app.core.pipeline.contracts import ObservationRecord, SystemStateContract
from app.core.state.trajectory import StateSnapshot, StateTrajectory


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    evidence_id: str
    source_ids: tuple[str, ...]
    epistemic_status: str
    contradiction: bool = False
    expected_but_not_observed: bool = False

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.source_ids or not self.epistemic_status:
            raise ValueError("evidence reference requires identity, sources and epistemic status")


@dataclass(frozen=True, slots=True)
class HypothesisReference:
    hypothesis_id: str
    status: str
    evidence_ids: tuple[str, ...]
    alternative_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ModelReference:
    model_id: str
    model_type: str
    version: str
    assumptions: tuple[str, ...]
    validity_window: tuple[datetime, datetime] | None = None
    calibrated: bool = False


@dataclass(frozen=True, slots=True)
class InterventionReference:
    intervention_id: str
    status: str
    target_ids: tuple[str, ...]
    started_at: datetime
    fidelity: float | None = None
    concurrent_intervention_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("started_at must be timezone-aware")
        if self.fidelity is not None and not 0.0 <= self.fidelity <= 1.0:
            raise ValueError("fidelity must be in [0,1]")


@dataclass(frozen=True, slots=True)
class SystemContext:
    """Immutable snapshot of the complete inferential context at one time."""

    system_id: str
    as_of: datetime
    state: StateSnapshot
    trajectory: StateTrajectory
    observations: tuple[ObservationRecord, ...]
    evidence: tuple[EvidenceReference, ...] = ()
    hypotheses: tuple[HypothesisReference, ...] = ()
    models: tuple[ModelReference, ...] = ()
    interventions: tuple[InterventionReference, ...] = ()
    contradictions: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    regimes: tuple[str, ...] = ()
    scales: tuple[str, ...] = ()
    structural_constraints: tuple[str, ...] = ()
    observation_process_version: str = "unknown"

    def __post_init__(self) -> None:
        if not self.system_id or self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise ValueError("system context requires system identity and timezone-aware as_of")
        if self.state.state.state_id != self.trajectory.latest.state.state_id if self.trajectory.latest else True:
            raise ValueError("state must equal trajectory latest snapshot")
        if self.state.state.as_of != self.as_of:
            raise ValueError("context as_of must equal current state as_of")

    @property
    def current_state(self) -> SystemStateContract:
        return self.state.state

    @property
    def observation_ids(self) -> frozenset[str]:
        return frozenset(item.observation_id for item in self.observations)

    @property
    def evidence_ids(self) -> frozenset[str]:
        return frozenset(item.evidence_id for item in self.evidence)

    @property
    def unresolved_hypotheses(self) -> tuple[HypothesisReference, ...]:
        return tuple(item for item in self.hypotheses if item.status not in {"DISPROVEN", "RETIRED"})


class SystemContextBuilder:
    """Builds an immutable context from the canonical state/trajectory spine."""

    def build(
        self,
        *,
        system_id: str,
        state: StateSnapshot,
        trajectory: StateTrajectory,
        observations: Iterable[ObservationRecord],
        evidence: Iterable[EvidenceReference] = (),
        hypotheses: Iterable[HypothesisReference] = (),
        models: Iterable[ModelReference] = (),
        interventions: Iterable[InterventionReference] = (),
        contradictions: Iterable[str] = (),
        missing_evidence: Iterable[str] = (),
        regimes: Iterable[str] = (),
        scales: Iterable[str] = (),
        structural_constraints: Iterable[str] = (),
        observation_process_version: str = "unknown",
    ) -> SystemContext:
        latest = trajectory.latest
        if latest is None or latest.state.state_id != state.state.state_id:
            raise ValueError("trajectory must contain the supplied current state")
        return SystemContext(
            system_id=system_id,
            as_of=state.state.as_of,
            state=state,
            trajectory=trajectory,
            observations=tuple(observations),
            evidence=tuple(evidence),
            hypotheses=tuple(hypotheses),
            models=tuple(models),
            interventions=tuple(interventions),
            contradictions=tuple(contradictions),
            missing_evidence=tuple(missing_evidence),
            regimes=tuple(regimes),
            scales=tuple(scales),
            structural_constraints=tuple(structural_constraints),
            observation_process_version=observation_process_version,
        )
