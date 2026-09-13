"""Incremental event-driven orchestration for the unified system kernel."""
from dataclasses import dataclass, field
from datetime import datetime
from .closed_loop import ClosedLoopEngine, ClosedLoopInput, SystemKernel
from .self_observation import SelfObservationReport

@dataclass(frozen=True, slots=True)
class RealtimeEvent:
    event_id: str
    event_time: datetime
    payload: object
    def __post_init__(self):
        if self.event_time.tzinfo is None: raise ValueError("event_time must be timezone-aware")

@dataclass(slots=True)
class RealtimeSystem:
    kernel: SystemKernel
    engine: ClosedLoopEngine = field(default_factory=ClosedLoopEngine)
    last_event_time: datetime | None = None

    def ingest(self, event: RealtimeEvent, cycle: ClosedLoopInput):
        if self.last_event_time is not None and event.event_time < self.last_event_time:
            raise ValueError("out-of-order event requires explicit replay/reconciliation")
        snapshot=self.engine.process_into(self.kernel, cycle)
        self.last_event_time=event.event_time
        return snapshot

    def inspect(self, report: SelfObservationReport) -> bool:
        """Fail closed when meta-observability identifies integrity degradation."""
        return not report.abstention_required
