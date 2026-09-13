from __future__ import annotations

from dataclasses import dataclass
from math import fabs

from app.core.pipeline.contracts import InteractionEffect, VariableState


@dataclass(frozen=True, slots=True)
class DynamicEdge:
    upstream: str
    downstream: str
    coupling: float
    lag_steps: int = 1


class DynamicInteractionGraph:
    def estimate(self, states: tuple[VariableState, ...], edges: tuple[DynamicEdge, ...]) -> tuple[InteractionEffect, ...]:
        by_name = {s.variable: s for s in states}
        out: list[InteractionEffect] = []
        for edge in edges:
            source = by_name.get(edge.upstream)
            if source is None or source.velocity is None:
                continue
            effect = edge.coupling * source.velocity
            out.append(InteractionEffect(edge.upstream, edge.downstream, edge.coupling, source.velocity, effect))
        return tuple(out)

    @staticmethod
    def structural_change(previous: tuple[DynamicEdge, ...], current: tuple[DynamicEdge, ...]) -> float:
        a = {(e.upstream, e.downstream): e.coupling for e in previous}
        b = {(e.upstream, e.downstream): e.coupling for e in current}
        keys = set(a) | set(b)
        return sum(fabs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys) / max(1, len(keys))
