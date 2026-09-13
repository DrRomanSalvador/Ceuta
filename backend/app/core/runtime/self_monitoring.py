"""Meta-monitoring of CeutIA itself."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class RuntimeHealth:
    component: str
    health: float
    drift: float
    latency_seconds: float
    errors: int
    abstentions: int
    healthy: bool

class SelfMonitoringEngine:
    def assess(self, component: str, *, health: float, drift: float=0.0, latency_seconds: float=0.0, errors: int=0, abstentions: int=0)->RuntimeHealth:
        ok=0<=health<=1 and drift<=.5 and errors==0 and latency_seconds>=0
        return RuntimeHealth(component,health,drift,latency_seconds,errors,abstentions,ok)
