"""Temporal semantics shared by all system inference stages."""
from dataclasses import dataclass
from datetime import datetime
from ..errors import ContractViolation, TemporalViolation

@dataclass(frozen=True, slots=True)
class TemporalPoint:
    event_time: datetime
    available_at: datetime
    sequence: int
    def __post_init__(self):
        if self.event_time.tzinfo is None or self.available_at.tzinfo is None: raise TemporalViolation("timestamps must be timezone-aware")
        if self.available_at < self.event_time: raise TemporalViolation("availability cannot precede event")
        if self.sequence < 0: raise ContractViolation("sequence must be nonnegative")

@dataclass(frozen=True, slots=True)
class TemporalWindow:
    start: datetime
    end: datetime
    aggregation: str = "none"
    sampling_interval_seconds: float | None = None
    def __post_init__(self):
        if self.start.tzinfo is None or self.end.tzinfo is None: raise TemporalViolation("window timestamps must be timezone-aware")
        if self.end <= self.start: raise TemporalViolation("window end must follow start")
        if self.sampling_interval_seconds is not None and self.sampling_interval_seconds <= 0: raise ContractViolation("sampling interval must be positive")

@dataclass(frozen=True, slots=True)
class DelayModel:
    delay_seconds: float
    distribution: str = "fixed"
    def __post_init__(self):
        if self.delay_seconds < 0: raise ContractViolation("delay cannot be negative")

@dataclass(frozen=True, slots=True)
class TemporalProcess:
    process_id: str
    windows: tuple[TemporalWindow, ...]
    delays: tuple[DelayModel, ...] = ()
    memory_horizon_seconds: float | None = None
    def __post_init__(self):
        if not self.process_id: raise ContractViolation("process_id required")
        if self.memory_horizon_seconds is not None and self.memory_horizon_seconds < 0: raise ContractViolation("memory horizon cannot be negative")
