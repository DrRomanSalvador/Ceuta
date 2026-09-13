"""Runtime resilience: capacity, degradation, checkpoint and recovery contracts."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class RuntimeMode(str,Enum):
    FULL="full"
    DEGRADED="degraded"
    READ_ONLY="read_only"
    ABSTAIN="abstain"

@dataclass(frozen=True,slots=True)
class Checkpoint:
    sequence:int
    event_hash:str
    state_hash:str
    model_versions:tuple[str,...]

@dataclass(frozen=True,slots=True)
class CapacityAssessment:
    utilization:float
    queue_depth:int
    mode:RuntimeMode
    reason:str

class ResilienceEngine:
    def capacity(self, utilization:float, queue_depth:int, *, max_utilization:float=.8, max_queue:int=100)->CapacityAssessment:
        if utilization<0 or queue_depth<0: raise ValueError("capacity metrics cannot be negative")
        if utilization>1 or queue_depth>max_queue*2: return CapacityAssessment(utilization,queue_depth,RuntimeMode.ABSTAIN,"capacity exhaustion")
        if utilization>max_utilization or queue_depth>max_queue: return CapacityAssessment(utilization,queue_depth,RuntimeMode.DEGRADED,"capacity pressure")
        return CapacityAssessment(utilization,queue_depth,RuntimeMode.FULL,"within capacity budget")

    @staticmethod
    def recover(checkpoint:Checkpoint, current_sequence:int)->bool:
        return current_sequence>=checkpoint.sequence
