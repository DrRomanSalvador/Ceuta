from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LineageEdge:
    parent_id: str
    child_id: str
    relation: str


class LineageGraph:
    def __init__(self) -> None:
        self._edges: list[LineageEdge] = []

    def add(self, edge: LineageEdge) -> None:
        if not edge.parent_id or not edge.child_id or not edge.relation:
            raise ValueError("lineage edge fields are required")
        self._edges.append(edge)

    def parents(self, child_id: str) -> tuple[LineageEdge, ...]:
        return tuple(e for e in self._edges if e.child_id == child_id)

    @property
    def edges(self) -> tuple[LineageEdge, ...]:
        return tuple(self._edges)
