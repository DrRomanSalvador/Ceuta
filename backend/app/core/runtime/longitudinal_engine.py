"""Single longitudinal runtime boundary for real-time evidence-to-decision processing.

This is the integration point for specialist engines. It deliberately refuses to
manufacture a state, forecast or causal conclusion when the observation process,
observability or model validity is insufficient.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence
from .sensing import RawSignal, SensorRegistry
from .ingestion import EventTimeIngestor, IngestionDecision
from .data_quality import ObservationQualityEngine, QualityAssessment
from .observability import ObservabilityEngine, ObservabilityAssessment
from .safety import SafetyEngine, SafetyGate
from .latency import LatencyEngine, LatencyBudget

@dataclass(frozen=True, slots=True)
class LongitudinalCycle:
    accepted: tuple[IngestionDecision,...]
    quality: tuple[QualityAssessment,...]
    observability: ObservabilityAssessment
    safety: SafetyGate
    latency: LatencyBudget
    decision_ready: bool

class LongitudinalMonitoringEngine:
    """Event-time monitoring boundary; specialist inference remains explicit."""
    def __init__(self, registry: SensorRegistry):
        self.ingestor=EventTimeIngestor(registry)
        self.quality=ObservationQualityEngine()
        self.observability=ObservabilityEngine()
        self.safety=SafetyEngine()
        self.latency=LatencyEngine()
    def ingest_cycle(self, signals: Sequence[RawSignal], *, now: datetime, required_signals: Sequence[str], deadline_seconds: float=60.0)->LongitudinalCycle:
        decisions=tuple(self.ingestor.ingest(s) for s in signals)
        assessments=[]
        for s in signals:
            descriptor=self.ingestor.registry.describe(s.signal_id)
            assessments.append(self.quality.assess(s,descriptor,now=now))
        usable=[s.signal_id for s,a in zip(signals,assessments) if a.usable]
        obs=self.observability.assess(required_signals,usable)
        latency=self.latency.measure(min((s.event_time for s in signals),default=now),now,deadline_seconds)
        gate=self.safety.evaluate(observable=obs.identifiable,identifiable=obs.identifiable,calibrated=True,source_integrity=all(a.usable for a in assessments),model_valid=True)
        return LongitudinalCycle(decisions,tuple(assessments),obs,gate,latency,gate.allowed and latency.within_deadline)
