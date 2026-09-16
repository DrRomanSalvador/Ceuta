"""A conservative directed causal graph with temporal and interaction semantics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import CausalEdge


@dataclass(frozen=True)
class GraphPath:
    nodes: tuple[str, ...]


class CausalGraph:
    def __init__(self, edges: Iterable[CausalEdge] = ()) -> None:
        self._edges: dict[tuple[str, str], CausalEdge] = {}
        for edge in edges:
            self.add(edge)

    @property
    def edges(self) -> tuple[CausalEdge, ...]:
        return tuple(self._edges.values())

    def add(self, edge: CausalEdge) -> None:
        if self.would_create_cycle(edge.cause, edge.effect, candidate_lag=edge.lag):
            raise ValueError("Causal graph must remain acyclic; temporal feedback requires every edge in the cycle to be lagged")
        self._edges[(edge.cause, edge.effect)] = edge

    def parents(self, node: str) -> tuple[str, ...]:
        return tuple(a for (a, b) in self._edges if b == node)

    def children(self, node: str) -> tuple[str, ...]:
        return tuple(b for (a, b) in self._edges if a == node)

    def ancestors(self, node: str) -> frozenset[str]:
        found: set[str] = set()
        stack = list(self.parents(node))
        while stack:
            current = stack.pop()
            if current in found:
                continue
            found.add(current)
            stack.extend(self.parents(current))
        return frozenset(found)

    def descendants(self, node: str) -> frozenset[str]:
        found: set[str] = set()
        stack = list(self.children(node))
        while stack:
            current = stack.pop()
            if current in found:
                continue
            found.add(current)
            stack.extend(self.children(current))
        return frozenset(found)

    def would_create_cycle(self, cause: str, effect: str, *, candidate_lag: float | None = None) -> bool:
        if cause == effect:
            return True
        # A contemporaneous cycle is forbidden. A dynamic feedback cycle is
        # representable only when the candidate edge and every edge on the
        # return path have strictly positive lags, corresponding to a
        # time-unrolled DAG rather than an instantaneous cyclic graph.
        stack: list[tuple[str, bool]] = [(cause, candidate_lag is not None and candidate_lag > 0)]
        visited: set[tuple[str, bool]] = set()
        while stack:
            node, all_lagged = stack.pop()
            state = (node, all_lagged)
            if state in visited:
                continue
            visited.add(state)
            if node == effect:
                if not all_lagged:
                    return True
                continue
            for child in self.children(node):
                edge = self._edges[(node, child)]
                edge_lagged = edge.lag is not None and edge.lag > 0
                stack.append((child, all_lagged and edge_lagged))
        return False

    def backdoor_candidates(self, exposure: str, outcome: str) -> tuple[str, ...]:
        """Return all observed ancestors of exposure that can open a backdoor path.

        Immediate parents are insufficient: a confounder may reach the exposure
        through one or more intermediate ancestors. This conservative candidate
        set intentionally over-includes ancestors; identification still requires
        explicit declaration and data/design assumptions in ``CausalIdentifier``.
        """
        return tuple(sorted(a for a in self.ancestors(exposure) if a != outcome))

    def interaction_candidates(self, variables: Iterable[str]) -> tuple[tuple[str, str], ...]:
        values = sorted(set(variables))
        return tuple((a, b) for i, a in enumerate(values) for b in values[i + 1 :])
