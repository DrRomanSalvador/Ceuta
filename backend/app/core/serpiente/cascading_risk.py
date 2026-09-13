from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CascadeStep:
    node: str
    risk: float


class CascadeRiskEngine:
    def propagate(self, seed: str, adjacency: dict[str, tuple[tuple[str, float], ...]], initial: float, *, threshold: float = 0.01) -> tuple[CascadeStep, ...]:
        if not 0.0 <= initial <= 1.0:
            raise ValueError("initial risk must be in [0,1]")
        risks = {seed: initial}
        frontier = [seed]
        while frontier:
            node = frontier.pop(0)
            for target, coupling in adjacency.get(node, ()):
                propagated = risks[node] * coupling
                if propagated < threshold:
                    continue
                if propagated > risks.get(target, 0.0):
                    risks[target] = min(1.0, propagated)
                    frontier.append(target)
        return tuple(CascadeStep(node, risk) for node, risk in sorted(risks.items()))
