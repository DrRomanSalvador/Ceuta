"""Temporal multilayer network representation for coupled systems."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class DynamicEdge:
    source: str
    target: str
    weight: float
    layer: str
    valid_from: datetime
    valid_to: datetime | None = None
    lag_seconds: float = 0.0
    causal_status: str = "unknown"

class DynamicNetwork:
    def __init__(self, edges: tuple[DynamicEdge,...]=()): self._edges=list(edges)
    def add(self, edge: DynamicEdge) -> None:
        if edge.source == edge.target: raise ValueError("self-edge is not permitted")
        if edge.weight != edge.weight: raise ValueError("weight must be finite")
        self._edges.append(edge)
    def active(self, at: datetime) -> tuple[DynamicEdge,...]:
        return tuple(e for e in self._edges if e.valid_from <= at and (e.valid_to is None or at < e.valid_to))
    def successors(self, node: str, at: datetime) -> tuple[DynamicEdge,...]:
        return tuple(e for e in self.active(at) if e.source == node)
