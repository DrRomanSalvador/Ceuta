from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceDependency:
    upstream: str
    downstream: str
    dependency: float

    def __post_init__(self) -> None:
        if not self.upstream or not self.downstream or self.upstream == self.downstream:
            raise ValueError("invalid source dependency endpoints")
        if not 0.0 <= self.dependency <= 1.0:
            raise ValueError("dependency must be in [0,1]")


class SourceDependencyGraph:
    def __init__(self) -> None:
        self._edges: dict[tuple[str, str], SourceDependency] = {}

    def add(self, edge: SourceDependency) -> None:
        self._edges[(edge.upstream, edge.downstream)] = edge

    def dependencies_of(self, source_id: str) -> tuple[SourceDependency, ...]:
        return tuple(e for e in self._edges.values() if e.downstream == source_id)

    def dependents_of(self, source_id: str) -> tuple[SourceDependency, ...]:
        return tuple(e for e in self._edges.values() if e.upstream == source_id)

    def is_mirror(self, upstream: str, downstream: str, threshold: float = 0.8) -> bool:
        edge = self._edges.get((upstream, downstream))
        return edge is not None and edge.dependency >= threshold

    @property
    def edges(self) -> tuple[SourceDependency, ...]:
        return tuple(sorted(self._edges.values(), key=lambda e: (e.upstream, e.downstream)))
