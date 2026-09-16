"""Persistent, executable scientific traceability graph.

Identifiers are deterministic projections of the existing corpus records and
runtime identifiers; this module does not create a second source/method registry.
Every edge is explicit and can be marked implemented, blocked, unsupported or
abstained without silently dropping a relationship.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import sqlite3


STATUSES = frozenset({"IMPLEMENTED", "COMPUTATIONALLY_TESTED", "INTERNALLY_VALIDATED", "PROSPECTIVELY_VALIDATED", "OPERATIONALLY_VALIDATED", "DOCUMENTED", "BLOCKED", "ABSTAINED", "NOT_APPLICABLE"})
NODE_KINDS = frozenset({"source", "claim", "constraint", "mechanism", "method", "data", "implementation", "runtime", "governance", "provenance", "cross_repo", "output", "outcome", "validation"})


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def stable_id(kind: str, *parts: str) -> str:
    if kind not in NODE_KINDS or not parts or any(not part for part in parts):
        raise ValueError("trace node kind and parts are required")
    return f"{kind}:{sha256(_canonical(parts).encode()).hexdigest()[:24]}"


@dataclass(frozen=True, slots=True)
class TraceNode:
    node_id: str
    kind: str
    label: str
    status: str
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in NODE_KINDS or self.status not in STATUSES or not self.node_id or not self.label:
            raise ValueError("invalid trace node")


@dataclass(frozen=True, slots=True)
class TraceEdge:
    from_id: str
    to_id: str
    relation: str
    status: str
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.from_id or not self.to_id or not self.relation or self.status not in STATUSES:
            raise ValueError("invalid trace edge")
        if self.from_id == self.to_id:
            raise ValueError("self trace edge is invalid")


class ScientificTraceGraph:
    """Durable graph over the existing scientific corpus and runtime IDs."""

    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS scientific_trace_nodes(node_id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL, status TEXT NOT NULL, metadata TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS scientific_trace_edges(from_id TEXT NOT NULL, to_id TEXT NOT NULL, relation TEXT NOT NULL, status TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(from_id,to_id,relation))")

    def add_node(self, node: TraceNode) -> None:
        with sqlite3.connect(self.storage_path) as db:
            existing = db.execute("SELECT kind,label,status,metadata FROM scientific_trace_nodes WHERE node_id=?", (node.node_id,)).fetchone()
            payload = _canonical(dict(node.metadata))
            if existing and existing != (node.kind, node.label, node.status, payload):
                raise ValueError("trace node is immutable")
            db.execute("INSERT OR IGNORE INTO scientific_trace_nodes VALUES(?,?,?,?,?)", (node.node_id, node.kind, node.label, node.status, payload))

    def add_edge(self, edge: TraceEdge) -> None:
        with sqlite3.connect(self.storage_path) as db:
            if not db.execute("SELECT 1 FROM scientific_trace_nodes WHERE node_id=?", (edge.from_id,)).fetchone() or not db.execute("SELECT 1 FROM scientific_trace_nodes WHERE node_id=?", (edge.to_id,)).fetchone():
                raise KeyError("both trace edge endpoints must exist")
            db.execute("INSERT OR IGNORE INTO scientific_trace_edges VALUES(?,?,?,?,?)", (edge.from_id, edge.to_id, edge.relation, edge.status, edge.reason))

    def edges_from(self, node_id: str) -> tuple[TraceEdge, ...]:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT from_id,to_id,relation,status,reason FROM scientific_trace_edges WHERE from_id=? ORDER BY to_id,relation", (node_id,)).fetchall()
        return tuple(TraceEdge(*row) for row in rows)

    def edges_to(self, node_id: str) -> tuple[TraceEdge, ...]:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT from_id,to_id,relation,status,reason FROM scientific_trace_edges WHERE to_id=? ORDER BY from_id,relation", (node_id,)).fetchall()
        return tuple(TraceEdge(*row) for row in rows)

    def verify_integrity(self) -> bool:
        with sqlite3.connect(self.storage_path) as db:
            nodes = db.execute("SELECT node_id,kind,label,status,metadata FROM scientific_trace_nodes ORDER BY node_id").fetchall()
            edges = db.execute("SELECT from_id,to_id,relation,status,reason FROM scientific_trace_edges ORDER BY from_id,to_id,relation").fetchall()
        try:
            node_ids = set()
            for node_id, kind, label, status, metadata in nodes:
                TraceNode(node_id, kind, label, status, tuple(sorted(json.loads(metadata).items())))
                node_ids.add(node_id)
            for row in edges:
                edge = TraceEdge(*row)
                if edge.from_id not in node_ids or edge.to_id not in node_ids:
                    return False
        except (ValueError, TypeError, json.JSONDecodeError):
            return False
        return True

    def missing_forward_links(self, source_id: str) -> tuple[str, ...]:
        """Return missing required downstream node kinds from a source."""
        kinds = {row[1] for row in self._reachable(source_id)}
        return tuple(kind for kind in ("claim", "constraint", "mechanism", "method", "data", "implementation", "runtime", "governance", "provenance", "cross_repo", "output", "outcome", "validation") if kind not in kinds)

    def _reachable(self, start: str) -> tuple[tuple[str, str], ...]:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT from_id,to_id FROM scientific_trace_edges").fetchall()
            nodes = db.execute("SELECT node_id,kind FROM scientific_trace_nodes").fetchall()
        adjacency: dict[str, list[str]] = {}
        for a, b in rows:
            adjacency.setdefault(a, []).append(b)
        kind = dict(nodes)
        seen = {start}; stack = [start]; result: list[tuple[str, str]] = []
        while stack:
            current = stack.pop()
            for nxt in adjacency.get(current, ()):
                if nxt not in seen:
                    seen.add(nxt); stack.append(nxt); result.append((nxt, kind.get(nxt, "")))
        return tuple(result)


__all__ = ["ScientificTraceGraph", "TraceEdge", "TraceNode", "stable_id", "STATUSES", "NODE_KINDS"]
