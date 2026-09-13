"""Pairwise, higher-order, temporal and multilayer relations."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class Relation:
    relation_id: str
    source: str
    targets: tuple[str, ...]
    kind: str
    strength: float
    lag_seconds: float = 0.0
    layer: str = "default"
    causal_status: str = "unknown"
    def __post_init__(self):
        if not self.relation_id or not self.source or not self.targets: raise ContractViolation("relation identity/endpoints required")
        if not 0 <= self.strength <= 1: raise ContractViolation("strength must be in [0,1]")
        if self.lag_seconds < 0: raise ContractViolation("lag cannot be negative")

@dataclass(frozen=True, slots=True)
class RelationSet:
    relations: tuple[Relation, ...]
    def by_layer(self, layer: str): return tuple(r for r in self.relations if r.layer == layer)
    def outgoing(self, source: str): return tuple(r for r in self.relations if r.source == source)
