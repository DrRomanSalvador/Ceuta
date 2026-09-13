"""Provenance/dependence graph for evidence synthesis in CeutIA."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceDependency:
    source_id: str
    depends_on: tuple[str, ...] = ()
    common_origin: str | None = None


class SourceDependenceGraph:
    """Represents dependence without assigning arbitrary statistical weights."""

    def __init__(self) -> None:
        self._nodes: dict[str, SourceDependency] = {}

    def add(self, dependency: SourceDependency) -> None:
        if not dependency.source_id.strip():
            raise ValueError("source_id is required")
        if dependency.source_id in dependency.depends_on:
            raise ValueError("a source cannot depend on itself")
        self._nodes[dependency.source_id] = dependency

    def is_dependent(self, source_id: str, other_id: str) -> bool:
        if source_id not in self._nodes or other_id not in self._nodes:
            return False
        seen: set[str] = set()
        stack = [source_id]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            node = self._nodes.get(current)
            if node is None:
                continue
            if other_id in node.depends_on:
                return True
            stack.extend(node.depends_on)
        a = self._nodes[source_id].common_origin
        b = self._nodes[other_id].common_origin
        return bool(a and b and a == b)

    def independent_sources(self, source_ids: tuple[str, ...]) -> tuple[str, ...]:
        selected: list[str] = []
        for source_id in source_ids:
            if not any(self.is_dependent(source_id, prior) or self.is_dependent(prior, source_id) for prior in selected):
                selected.append(source_id)
        return tuple(selected)

    def common_origin_clusters(self, source_ids: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
        clusters: dict[str, list[str]] = {}
        for source_id in source_ids:
            origin = self._nodes.get(source_id).common_origin if source_id in self._nodes else None
            key = origin or f"source:{source_id}"
            clusters.setdefault(key, []).append(source_id)
        return tuple(tuple(items) for items in clusters.values())


__all__ = ["SourceDependenceGraph", "SourceDependency"]
