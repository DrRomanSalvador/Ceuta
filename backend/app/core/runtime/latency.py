"""Latency accounting from sensing to decision."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class LatencyBudget:
    ingestion_seconds: float
    state_seconds: float
    inference_seconds: float
    decision_seconds: float
    intervention_seconds: float
    deadline_seconds: float
    @property
    def total_seconds(self)->float:
        return sum((self.ingestion_seconds,self.state_seconds,self.inference_seconds,self.decision_seconds,self.intervention_seconds))
    @property
    def within_deadline(self)->bool: return self.total_seconds <= self.deadline_seconds

class LatencyEngine:
    def measure(self,event_time:datetime,decision_time:datetime,deadline_seconds:float)->LatencyBudget:
        if event_time.tzinfo is None or event_time.utcoffset() is None or decision_time.tzinfo is None or decision_time.utcoffset() is None:
            raise ValueError("latency timestamps must be timezone-aware")
        if deadline_seconds < 0: raise ValueError("deadline cannot be negative")
        total=(decision_time-event_time).total_seconds()
        if total < 0: raise ValueError("decision time cannot precede event time")
        return LatencyBudget(total,0.0,0.0,0.0,0.0,deadline_seconds)
