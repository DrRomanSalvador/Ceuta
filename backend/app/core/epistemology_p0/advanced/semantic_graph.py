"""CeutIA Layer 2 semantic graph.

The graph represents relationships between already-controlled observations,
claims and hypotheses. Relationship type is deliberately separate from the
canonical epistemic state machine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid

from ..observation_boundary import admit_observation
from ..p0_contracts import EvidenceContract
from .hypotheses import Hypothesis


class NodeKind(str, Enum):
    SOURCE = "source"
    DOCUMENT = "document"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    ENTITY = "entity"
    EVENT = "event"
    VARIABLE = "variable"
    LOCATION = "location"
    HYPOTHESIS = "hypothesis"


class EdgeKind(str, Enum):
    EXTRACTED_FROM = "extracted_from"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    ASSOCIATION = "association"
    TEMPORAL_PRECEDENCE = "temporal_precedence"
    SOURCE_DEPENDENCY = "source_dependency"
    CAUSAL_HYPOTHESIS = "causal_hypothesis"
    CAUSALITY_SUPPORTED = "causality_supported"
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
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

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
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

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
    """Directed append-friendly graph with explicit causal safeguards."""

    _CAUSAL_FIELDS = {
        "hypothesis_id",
        "mechanism",
        "evidence_ids",
        "alternative_explanations",
        "predictions",
        "falsification_criterion",
    }

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
        edge_properties = properties or {}
        if kind in {EdgeKind.CAUSAL_HYPOTHESIS, EdgeKind.CAUSALITY_SUPPORTED}:
            self._validate_causal_edge(kind, edge_properties)
        if kind is EdgeKind.TEMPORAL_PRECEDENCE:
            self._validate_temporal_edge(edge_properties)
        if kind is EdgeKind.SOURCE_DEPENDENCY:
            self._validate_source_dependency(edge_properties)

        eid = edge_id or f"e-{uuid.uuid4().hex[:10]}"
        edge = GraphEdge(eid, kind, from_id, to_id, weight, edge_properties)
        self.edges[eid] = edge
        self._out.setdefault(from_id, []).append(eid)
        self._in.setdefault(to_id, []).append(eid)
        return edge

    def add_evidence_contract(
        self,
        evidence: EvidenceContract,
        *,
        evaluation_time: datetime,
    ) -> GraphNode:
        """Integrate only a temporally eligible canonical P0 evidence contract."""
        admitted, eligibility = admit_observation(evidence, evaluation_time=evaluation_time)
        source = self.add_node(
            NodeKind.SOURCE,
            admitted.source_id,
            admitted.source_id,
            {"source_relation": admitted.source_relation.value},
        )
        claim = self.add_node(
            NodeKind.CLAIM,
            admitted.claim,
            f"claim-{admitted.evidence_id}",
            {
                "epistemic_status": admitted.epistemic_status.value,
                "available_at": admitted.available_at.isoformat(),
            },
        )
        evidence_node = self.add_node(
            NodeKind.EVIDENCE,
            admitted.evidence_id,
            admitted.evidence_id,
            {
                "epistemic_status": admitted.epistemic_status.value,
                "available_at": admitted.available_at.isoformat(),
                "eligible_at": eligibility.evaluation_time.isoformat(),
                "source_relation": admitted.source_relation.value,
                "uncertainty": admitted.uncertainty.model_dump(mode="json"),
                "provenance": [item.model_dump(mode="json") for item in admitted.provenance],
            },
        )
        self.add_edge(EdgeKind.SUPPORTS, evidence_node.node_id, claim.node_id)
        self.add_edge(EdgeKind.ABOUT, evidence_node.node_id, source.node_id)
        if admitted.event_time is not None:
            event_id = f"event-{admitted.evidence_id}"
            self.add_node(
                NodeKind.EVENT,
                admitted.event_time.isoformat(),
                event_id,
                {"event_time": admitted.event_time.isoformat()},
            )
            self.add_edge(EdgeKind.ABOUT, evidence_node.node_id, event_id)
        return evidence_node

    def add_hypothesis(self, hypothesis: Hypothesis) -> GraphNode:
        return self.add_node(
            NodeKind.HYPOTHESIS,
            hypothesis.statement,
            hypothesis.hypothesis_id,
            hypothesis.to_dict(),
        )

    def _validate_causal_edge(self, kind: EdgeKind, properties: Dict[str, Any]) -> None:
        missing = [field for field in self._CAUSAL_FIELDS if not properties.get(field)]
        if missing:
            raise ValueError(
                f"{kind.value} requires explicit mechanism, evidence, alternatives, "
                f"predictions and falsification criterion: missing={missing}"
            )
        if kind is EdgeKind.CAUSALITY_SUPPORTED and not properties.get("validation_method"):
            raise ValueError("causality_supported requires a validation_method")
        if properties.get("causality_confirmed") is True:
            raise ValueError("CAUSALITY_CONFIRMED is not a permitted default graph state")

    @staticmethod
    def _validate_temporal_edge(properties: Dict[str, Any]) -> None:
        earlier = properties.get("earlier_time")
        later = properties.get("later_time")
        if earlier is None or later is None:
            raise ValueError("temporal_precedence requires earlier_time and later_time")
        if earlier >= later:
            raise ValueError("temporal_precedence requires earlier_time < later_time")

    @staticmethod
    def _validate_source_dependency(properties: Dict[str, Any]) -> None:
        relation = properties.get("relation")
        if relation not in {"DEPENDENT", "COPY", "AMPLIFIER", "UNKNOWN"}:
            raise ValueError("source_dependency requires an explicit dependency relation")

    def neighbors(
        self,
        node_id: str,
        *,
        direction: str = "out",
        edge_kind: Optional[EdgeKind] = None,
    ) -> List[GraphNode]:
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
        if claim_id not in self.nodes:
            return {"nodes": [], "edges": []}
        related_nodes: Set[str] = {claim_id}
        related_edges: Set[str] = set()
        for eid in self._out.get(claim_id, []) + self._in.get(claim_id, []):
            related_edges.add(eid)
            edge = self.edges[eid]
            related_nodes.add(edge.from_id)
            related_nodes.add(edge.to_id)
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
        for node in self.nodes.values():
            by_kind[node.kind.value] = by_kind.get(node.kind.value, 0) + 1
        return {"nodes": len(self.nodes), "edges": len(self.edges), "nodes_by_kind": by_kind}

    def to_dict(self) -> dict:
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
            "stats": self.stats(),
        }
