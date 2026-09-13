"""
CeutIA - Modelo de Independencia de Fuentes (P0)

La corroboración debe ponderar la independencia real.
Diez medios que reproducen el mismo comunicado no equivalen a diez confirmaciones.
Se modela como red de relaciones, no como contador simple.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime


class SourceRole(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    AGGREGATOR = "aggregator"
    UNKNOWN = "unknown"


class DependenceType(str, Enum):
    SAME_SOURCE = "same_source"
    SHARED_COMMUNIQUE = "shared_communique"
    TEXTUAL_COPY = "textual_copy"
    NEAR_COPY = "near_copy"
    CITATION_CHAIN = "citation_chain"
    SHARED_INTEREST = "shared_interest"
    SAME_METHOD = "same_method"
    TEMPORAL_COINCIDENCE = "temporal_coincidence"
    INDEPENDENT = "independent"
    UNKNOWN = "unknown"


@dataclass
class SourceNode:
    source_id: str
    name: str
    role: SourceRole = SourceRole.UNKNOWN
    known_interests: List[str] = field(default_factory=list)
    known_links: List[str] = field(default_factory=list)
    methodology_notes: Optional[str] = None
    reliability_base: float = 0.5


@dataclass
class DependenceEdge:
    source_a: str
    source_b: str
    dependence_type: DependenceType
    strength: float
    evidence: Optional[str] = None
    detected_at: Optional[datetime] = None


class SourceIndependenceGraph:
    """Grafo de independencia de fuentes. Corroboración como red, no contador."""

    def __init__(self):
        self.nodes: Dict[str, SourceNode] = {}
        self.edges: List[DependenceEdge] = []
        self._adj: Dict[str, Dict[str, DependenceEdge]] = {}

    def add_source(self, node: SourceNode) -> None:
        self.nodes[node.source_id] = node
        if node.source_id not in self._adj:
            self._adj[node.source_id] = {}

    def add_dependence(self, edge: DependenceEdge) -> None:
        self.edges.append(edge)
        self._adj.setdefault(edge.source_a, {})[edge.source_b] = edge
        self._adj.setdefault(edge.source_b, {})[edge.source_a] = edge

    def get_dependence(self, source_a: str, source_b: str) -> Optional[DependenceEdge]:
        return self._adj.get(source_a, {}).get(source_b)

    def independence_score(self, source_a: str, source_b: str) -> float:
        if source_a == source_b:
            return 0.0
        edge = self.get_dependence(source_a, source_b)
        if edge is None:
            return 0.7
        return max(0.0, 1.0 - edge.strength)

    def detect_shared_communique_cluster(self, source_ids: List[str]) -> List[List[str]]:
        clusters: List[Set[str]] = []
        visited: Set[str] = set()
        for sid in source_ids:
            if sid in visited:
                continue
            cluster = {sid}
            stack = [sid]
            while stack:
                current = stack.pop()
                for other, edge in self._adj.get(current, {}).items():
                    if other in source_ids and other not in cluster:
                        if edge.dependence_type in (
                            DependenceType.SHARED_COMMUNIQUE,
                            DependenceType.TEXTUAL_COPY,
                            DependenceType.NEAR_COPY,
                            DependenceType.SAME_SOURCE,
                        ):
                            cluster.add(other)
                            stack.append(other)
            visited.update(cluster)
            if len(cluster) > 1:
                clusters.append(list(cluster))
        return clusters

    def effective_corroboration_weight(
        self,
        source_ids: List[str],
        base_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        if not source_ids:
            return 0.0
        unique = list(dict.fromkeys(source_ids))
        if len(unique) == 1:
            return (base_weights or {}).get(unique[0], 1.0)
        weights = base_weights or {}
        clusters = self.detect_shared_communique_cluster(unique)
        clustered_ids: set = set()
        for c in clusters:
            clustered_ids.update(c)
        effective = 0.0
        for cluster in clusters:
            best = max(weights.get(s, 1.0) for s in cluster)
            effective += best
        independents = [s for s in unique if s not in clustered_ids]
        for s in independents:
            others = [o for o in unique if o != s]
            if not others:
                indep = 1.0
            else:
                indep = sum(self.independence_score(s, o) for o in others) / len(others)
            effective += weights.get(s, 1.0) * max(0.15, indep)
        if effective == 0.0 and unique:
            effective = max(weights.get(s, 1.0) for s in unique)
        return round(effective, 4)

    def to_dict(self) -> dict:
        return {
            "nodes": {
                sid: {
                    "source_id": n.source_id,
                    "name": n.name,
                    "role": n.role.value,
                    "known_interests": n.known_interests,
                    "known_links": n.known_links,
                    "reliability_base": n.reliability_base,
                }
                for sid, n in self.nodes.items()
            },
            "edges": [
                {
                    "source_a": e.source_a,
                    "source_b": e.source_b,
                    "dependence_type": e.dependence_type.value,
                    "strength": e.strength,
                    "evidence": e.evidence,
                }
                for e in self.edges
            ],
        }
