"""Sequential change-point and regime diagnostics with explicit uncertainty limits."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Sequence

@dataclass(frozen=True, slots=True)
class ChangePoint:
    index: int
    score: float
    before_mean: float
    after_mean: float
    method: str

class ChangePointEngine:
    def detect(self, values: Sequence[float], *, min_segment: int = 5, threshold: float = 3.0) -> tuple[ChangePoint, ...]:
        if min_segment < 2 or len(values) < 2*min_segment: return ()
        x = tuple(float(v) for v in values)
        candidates=[]
        for i in range(min_segment, len(x)-min_segment+1):
            left,right=x[:i],x[i:]
            pooled=max(sqrt(sum((v-mean(x))**2 for v in x)/max(1,len(x)-1)),1e-12)
            score=abs(mean(right)-mean(left))/pooled
            if score>=threshold:
                candidates.append(ChangePoint(i,score,mean(left),mean(right),"mean-shift-standardized"))
        return tuple(candidates)
