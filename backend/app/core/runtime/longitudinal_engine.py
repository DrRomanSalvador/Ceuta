"""Single longitudinal runtime boundary for real-time evidence-to-decision processing.

This is the integration point for specialist engines. It deliberately refuses to
manufacture a state, forecast or causal conclusion when the observation process,
observability or model validity is insufficient.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from .data_quality import ObservationQualityEngine, QualityAssessment
from .ingestion import EventTimeIngestor, IngestionDecision
from .latency import LatencyBudget, LatencyEngine
from .observability import ObservabilityAssessment, ObservabilityEngine
from .sensing import RawSignal, SensorRegistry
from .safety import SafetyEngine, SafetyGate


@dataclass(frozen=True, slots=True)
class LongitudinalCycle:
    accepted: tuple[IngestionDecision, ...]
    quality: tuple[QualityAssessment, ...]
    observability: ObservabilityAssessment
    safety: SafetyGate
    latency: LatencyBudget
    decision_ready: bool


class LongitudinalMonitoringEngine:
    """Event-time monitoring boundary; specialist inference remains explicit."""

    def __init__(self, registry: SensorRegistry):
        self.ingestor = EventTimeIngestor(registry)
        self.quality = ObservationQualityEngine()
        self.observability = ObservabilityEngine()
        self.safety = SafetyEngine()
        self.latency = LatencyEngine()

    def ingest_cycle(
        self,
        signals: Sequence[RawSignal],
        *,
        now: datetime,
        required_signals: Sequence[str],
        deadline_seconds: float = 60.0,
    ) -> LongitudinalCycle:
        decisions: list[IngestionDecision] = []
        accepted_signals: list[RawSignal] = []
        for signal in signals:
            try:
                decision = self.ingestor.ingest(signal)
            except Exception as exc:
                decision = IngestionDecision(False, f"rejected: {type(exc).__name__}")
            decisions.append(decision)
            if decision.accepted:
                accepted_signals.append(signal)

        assessments: list[QualityAssessment] = []
        for signal in accepted_signals:
            descriptor = self.ingestor.registry.describe(signal.signal_id)
            assessments.append(self.quality.assess(signal, descriptor, now=now))
        usable = [
            signal.signal_id
            for signal, assessment in zip(accepted_signals, assessments)
            if assessment.usable
        ]
        obs = self.observability.assess(required_signals, usable)
        event_times = [signal.event_time for signal in accepted_signals]
        latency = self.latency.measure(min(event_times, default=now), now, deadline_seconds)
        source_integrity = bool(assessments) and all(assessment.usable for assessment in assessments)
        gate = self.safety.evaluate(
            observable=obs.identifiable,
            identifiable=obs.identifiable,
            calibrated=False,
            source_integrity=source_integrity,
            model_valid=False,
        )
        return LongitudinalCycle(
            tuple(decisions),
            tuple(assessments),
            obs,
            gate,
            latency,
            gate.allowed and latency.within_deadline,
        )
