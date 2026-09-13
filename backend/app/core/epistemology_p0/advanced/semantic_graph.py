"""
P2 — Grafo semántico de conocimiento epistemológico.

Nodos: Source, Document, Claim, Evidence, Entity, Event, Variable.
Aristas: EXTRACTED_FROM, SUPPORTS, CONTRADICTS, DEPENDS_ON, ABOUT, SAME_AS, etc.
No infiere verdad; solo estructura relaciones auditables.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Iterable
from datetime import datetime, timezone
import uuid


class NodeKind(str, Enum):
    SOURCE = "source"
    DOCUMENT = "document"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    ENTITY = "entity"
    EVENT = "event"
    VARIABLE = "variable"
    LOCATION = "location"


class EdgeKind(str, Enum):
    EXTRACTED_FROM = "extracted_from"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    ABOUT = "about"
    SAME_AS = "same_as"
    DERIVED_FROM = "derived_from"
    MEASURES = "measures"
    LOCATED_IN = "located_in"
    PUBLISHED_BY = "published_by"


@dataclass
class GraphNode:
    node_id: str
    kind: NodeKind
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at,
        }


@dataclass
class GraphEdge:
    edge_id: str
    kind: EdgeKind
    from_id: str
    to_id: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "kind": self.kind.value,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at,
        }


class SemanticGraph:
    """Grafo dirigido etiquetado. Append-friendly; no borra historia."""

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self._out: Dict[str, List[str]] = {}
        self._in: Dict[str, List[str]] = {}

    def add_node(
        self,
        kind: NodeKind,
        label: str,
        node_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> GraphNode:
        nid = node_id or f"{kind.value}-{uuid.uuid4().hex[:10]}"
        if nid in self.nodes:
            # merge properties (no borrar)
            existing = self.nodes[nid]
            existing.properties.update(properties or {})
            return existing
        node = GraphNode(nid, kind, label, properties or {})
        self.nodes[nid] = node
        self._out.setdefault(nid, [])
        self._in.setdefault(nid, [])
        return node

    def add_edge(
        self,
        kind: EdgeKind,
        from_id: str,
        to_id: str,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None,
        edge_id: Optional[str] = None,
    ) -> GraphEdge:
        if from_id not in self.nodes or to_id not in self.nodes:
            raise KeyError("both endpoints must exist")
        eid = edge_id or f"e-{uuid.uuid4().hex[:10]}"
        edge = GraphEdge(eid, kind, from_id, to_id, weight, properties or {})
        self.edges[eid] = edge
        self._out.setdefault(from_id, []).append(eid)
        self._in.setdefault(to_id, []).append(eid)
        return edge

    def neighbors(self, node_id: str, *, direction: str = "out", edge_kind: Optional[EdgeKind] = None) -> List[GraphNode]:
        ids = self._out.get(node_id, []) if direction == "out" else self._in.get(node_id, [])
        result = []
        for eid in ids:
            edge = self.edges[eid]
            if edge_kind and edge.kind != edge_kind:
                continue
            other = edge.to_id if direction == "out" else edge.from_id
            if other in self.nodes:
                result.append(self.nodes[other])
        return result

    def subgraph_for_claim(self, claim_id: str) -> dict:
        """Subgrafo centrado en un claim (1 hop + evidencias)."""
        if claim_id not in self.nodes:
            return {"nodes": [], "edges": []}
        related_nodes: Set[str] = {claim_id}
        related_edges: Set[str] = set()
        for eid in self._out.get(claim_id, []) + self._in.get(claim_id, []):
            related_edges.add(eid)
            e = self.edges[eid]
            related_nodes.add(e.from_id)
            related_nodes.add(e.to_id)
        return {
            "nodes": [self.nodes[n].to_dict() for n in related_nodes if n in self.nodes],
            "edges": [self.edges[e].to_dict() for e in related_edges],
        }

    def link_evidence_chain(
        self,
        *,
        source_id: str,
        source_label: str,
        document_id: str,
        document_label: str,
        claim_id: str,
        claim_label: str,
        evidence_id: str,
        evidence_label: str,
        variable: Optional[str] = None,
    ) -> None:
        """Cadena canónica SOURCE → DOCUMENT → CLAIM → EVIDENCE (+ VARIABLE)."""
        self.add_node(NodeKind.SOURCE, source_label, source_id)
        self.add_node(NodeKind.DOCUMENT, document_label, document_id)
        self.add_node(NodeKind.CLAIM, claim_label, claim_id)
        self.add_node(NodeKind.EVIDENCE, evidence_label, evidence_id)
        self.add_edge(EdgeKind.PUBLISHED_BY, document_id, source_id)
        self.add_edge(EdgeKind.EXTRACTED_FROM, claim_id, document_id)
        self.add_edge(EdgeKind.SUPPORTS, evidence_id, claim_id)
        if variable:
            vid = f"var-{variable}"
            self.add_node(NodeKind.VARIABLE, variable, vid)
            self.add_edge(EdgeKind.MEASURES, evidence_id, vid)

    def stats(self) -> dict:
        by_kind: Dict[str, int] = {}
        for n in self.nodes.values():
            by_kind[n.kind.value] = by_kind.get(n.kind.value, 0) + 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "nodes_by_kind": by_kind,
        }

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges.values()],
            "stats": self.stats(),
        }
