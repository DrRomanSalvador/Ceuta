from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_METERS = 6_371_008.8


@dataclass(frozen=True, slots=True)
class SpatialNode:
    node_id: str
    latitude: float
    longitude: float
    risk: float

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be in [-90,90]")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be in [-180,180]")
        if not 0.0 <= self.risk <= 1.0:
            raise ValueError("risk must be in [0,1]")


class SpatialEngine:
    @staticmethod
    def distance(a: SpatialNode, b: SpatialNode) -> float:
        """Great-circle distance between two WGS84-like geographic coordinates."""
        lat1, lat2 = radians(a.latitude), radians(b.latitude)
        dlat = lat2 - lat1
        dlon = radians(b.longitude - a.longitude)
        haversine = sin(dlat / 2.0) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2.0) ** 2
        return 2.0 * EARTH_RADIUS_METERS * asin(sqrt(min(1.0, haversine)))

    def propagate(self, nodes: tuple[SpatialNode, ...], *, radius: float) -> tuple[SpatialNode, ...]:
        if radius < 0.0:
            raise ValueError("radius must be non-negative")
        out: list[SpatialNode] = []
        for node in nodes:
            influence = max(
                (other.risk for other in nodes if other.node_id != node.node_id and self.distance(node, other) <= radius),
                default=0.0,
            )
            out.append(SpatialNode(node.node_id, node.latitude, node.longitude, max(node.risk, influence)))
        return tuple(out)
