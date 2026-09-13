"""Scientific execution boundary for CeutIA's longitudinal closed loop.

The pipeline enforces the epistemic ordering:
observation -> quality/integrity -> observability -> state -> prediction/causal
analysis -> decision -> intervention -> outcome learning. Specialist engines are
injected explicitly. No stage may fabricate a missing upstream result.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Mapping, Sequence

from .integrity import IntegrityAssessment
from .longitudinal_engine import LongitudinalCycle, LongitudinalMonitoringEngine
from .official_sources import OfficialSourceRegistry
from .scientific_guards import ScientificIntegrityEngine


class PipelineDisposition(str, Enum):
    PROCEED = "proceed"
    ABSTAIN = "abstain"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True, slots=True)
class SpecialistResult:
    name: str
    epistemic_level: str
    value: Any
    assumptions: tuple[str, ...]
    provenance: tuple[str, ...]
    valid: bool


@dataclass(frozen=True, slots=True)
class ScientificPipelineResult:
    cycle: LongitudinalCycle
    specialists: tuple[SpecialistResult, ...]
    disposition: PipelineDisposition
    blocking_reasons: tuple[str, ...]
    source_freshness: tuple[Any, ...]


class ScientificLongitudinalPipeline:
    """Deterministic orchestration with fail-closed scientific gates."""

    def __init__(self, monitor: LongitudinalMonitoringEngine,
                 sources: OfficialSourceRegistry,
                 scientific_guard: ScientificIntegrityEngine) -> None:
        self.monitor = monitor
        self.sources = sources
        self.guard = scientific_guard

    def run(self, signals: Sequence[Any], *, now: datetime,
            required_signals: Sequence[str], deadline_seconds: float,
            source_required: bool = False,
            integrity: IntegrityAssessment | None = None,
            specialists: Mapping[str, Callable[[LongitudinalCycle], SpecialistResult]] | None = None,
            require_human_review: bool = False) -> ScientificPipelineResult:
        cycle = self.monitor.ingest_cycle(signals, now=now, required_signals=required_signals,
                                          deadline_seconds=deadline_seconds)
        freshness = self.sources.freshness(now)
        blockers: list[str] = []
        if not cycle.decision_ready:
            blockers.append("real-time cycle is not decision-ready")
        if source_required and any(not item.current for item in freshness):
            blockers.append("one or more required official sources are stale or unverified")
        if integrity is not None and not integrity.accepted:
            blockers.append("source/data integrity gate failed")

        results: list[SpecialistResult] = []
        if not blockers and specialists:
            for name, runner in specialists.items():
                try:
                    result = runner(cycle)
                except Exception as exc:
                    blockers.append(f"specialist {name} failed: {type(exc).__name__}")
                    continue
                if result.name != name or not result.valid:
                    blockers.append(f"specialist {name} returned an invalid result")
                    continue
                results.append(result)

        if blockers:
            disposition = PipelineDisposition.ABSTAIN
        elif require_human_review:
            disposition = PipelineDisposition.HUMAN_REVIEW
        else:
            disposition = PipelineDisposition.PROCEED
        return ScientificPipelineResult(cycle, tuple(results), disposition, tuple(blockers), tuple(freshness))
