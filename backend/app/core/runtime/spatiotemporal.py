"""Spatial and spatiotemporal runtime contracts with explicit coordinate semantics."""
from __future__ import annotations
from dataclasses import dataclass
from math import asin,cos,radians,sin,sqrt
from datetime import datetime

EARTH_RADIUS_M=6_371_008.8

@dataclass(frozen=True,slots=True)
class SpatialObservation:
    observation_id:str
    latitude:float
    longitude:float
    observed_at:datetime
    value:float
    region:str|None=None
    def __post_init__(self):
        if not -90<=self.latitude<=90 or not -180<=self.longitude<=180: raise ValueError("invalid geographic coordinates")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None: raise ValueError("observed_at must be timezone-aware")

class SpatialTemporalEngine:
    @staticmethod
    def distance_m(a:SpatialObservation,b:SpatialObservation)->float:
        p1,p2=radians(a.latitude),radians(b.latitude); dp=radians(b.latitude-a.latitude); dl=radians(b.longitude-a.longitude)
        h=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
        return 2*EARTH_RADIUS_M*asin(sqrt(h))
    def lagged_pair(self,a:SpatialObservation,b:SpatialObservation,max_distance_m:float,max_lag_seconds:float)->bool:
        return self.distance_m(a,b)<=max_distance_m and abs((a.observed_at-b.observed_at).total_seconds())<=max_lag_seconds
