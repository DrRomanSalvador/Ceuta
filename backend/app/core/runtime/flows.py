"""Capacity, queues and bottleneck monitoring."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class FlowState:
    capacity: float
    load: float
    queue: float
    inflow: float
    outflow: float
    @property
    def utilization(self)->float: return self.load/self.capacity if self.capacity>0 else float("inf")
    @property
    def reserve(self)->float: return self.capacity-self.load-self.queue

class FlowEngine:
    def step(self, state:FlowState, inflow:float, outflow:float)->FlowState:
        queue=max(0.0,state.queue+inflow-outflow)
        return FlowState(state.capacity,state.load+inflow-outflow,queue,inflow,outflow)
