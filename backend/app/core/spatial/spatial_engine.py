from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True, slots=True)
class SpatialNode:
    node_id: str
    latitude: float
    longitude: float
    risk: float


class SpatialEngine:
    @staticmethod
    def distance(a: SpatialNode, b: SpatialNode) -> float:
        return hypot(a.latitude - b.latitude, a.longitude - b.longitude)

    def propagate(self, nodes: tuple[SpatialNode, ...], *, radius: float) -> tuple[SpatialNode, ...]:
        out: list[SpatialNode] = []
        for node in nodes:
            influence = max((other.risk for other in nodes if other.node_id != node.node_id and self.distance(node, other) <= radius), default=0.0)
            out.append(SpatialNode(node.node_id, node.latitude, node.longitude, max(node.risk, influence)))
        return tuple(out)
