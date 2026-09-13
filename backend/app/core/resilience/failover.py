from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NodeHealth:
    node_id: str
    healthy: bool
    priority: int


class FailoverController:
    def select(self, nodes: tuple[NodeHealth, ...]) -> NodeHealth:
        healthy = tuple(n for n in nodes if n.healthy)
        if not healthy:
            raise RuntimeError("no healthy failover node available")
        return min(healthy, key=lambda n: n.priority)
