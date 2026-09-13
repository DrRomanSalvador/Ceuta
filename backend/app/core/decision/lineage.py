"""Explicit lineage contracts for reproducible CeutIA decision lifecycles."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping
import json
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class LineageNode:
    """One immutable lifecycle stage and its declared dependencies."""

    node_id: str
    stage: str
    input_refs: tuple[str, ...] = ()
    output_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    model_refs: tuple[str, ...] = ()
    policy_refs: tuple[str, ...] = ()
    configuration_hash: str = ""
    code_revision: str = ""
    as_of: str = ""
    execution_id: str | None = None

    def __post_init__(self) -> None:
        if not self.node_id.strip():
            raise ValueError("lineage node requires node_id")
        if not self.stage.strip():
            raise ValueError("lineage node requires stage")
        if not self.configuration_hash.strip():
            raise ValueError("lineage node requires configuration_hash")
        if not self.code_revision.strip():
            raise ValueError("lineage node requires code_revision")
        if not self.as_of.strip():
            raise ValueError("lineage node requires as_of")


@dataclass(frozen=True, slots=True)
class DecisionLineage:
    """Complete ordered lineage for a single decision lifecycle."""

    decision_id: str
    nodes: tuple[LineageNode, ...]
    terminal_disposition: str
    semantic_identity: str

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("lineage requires decision_id")
        if not self.nodes:
            raise ValueError("lineage requires at least one node")
        if not self.terminal_disposition.strip():
            raise ValueError("lineage requires terminal disposition")
        if not self.semantic_identity.strip():
            raise ValueError("lineage requires semantic identity")
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("lineage node IDs must be unique")

    def semantic_payload(self) -> dict[str, Any]:
        """Return deterministic lineage identity without execution-only metadata."""
        nodes = []
        for node in self.nodes:
            payload = asdict(node)
            payload.pop("execution_id", None)
            nodes.append(payload)
        return {
            "decision_id": self.decision_id,
            "nodes": nodes,
            "terminal_disposition": self.terminal_disposition,
            "semantic_identity": self.semantic_identity,
        }

    def execution_payload(self) -> dict[str, Any]:
        """Return the complete lineage including execution metadata."""
        return {
            "decision_id": self.decision_id,
            "nodes": [asdict(node) for node in self.nodes],
            "terminal_disposition": self.terminal_disposition,
            "semantic_identity": self.semantic_identity,
        }

    def semantic_fingerprint(self) -> str:
        canonical = json.dumps(
            self.semantic_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return sha256(canonical).hexdigest()

    def execution_fingerprint(self) -> str:
        canonical = json.dumps(
            self.execution_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return sha256(canonical).hexdigest()


__all__ = ["DecisionLineage", "LineageNode"]
