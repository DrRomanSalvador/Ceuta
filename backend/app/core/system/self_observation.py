"""Meta-observability of CeutIA's own inference process."""
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SelfObservation:
    component: str
    health: str
    uncertainty: float
    assumption_violations: tuple[str, ...] = ()
    drift_flags: tuple[str, ...] = ()
    observability_gaps: tuple[str, ...] = ()
    contamination_flags: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class SelfObservationReport:
    observations: tuple[SelfObservation, ...]
    abstention_required: bool
    reasons: tuple[str, ...]

    @classmethod
    def from_observations(cls, observations):
        items=tuple(observations)
        reasons=tuple(f"{x.component}: inference integrity degraded" for x in items if x.assumption_violations or x.contamination_flags or x.observability_gaps)
        return cls(items, bool(reasons), reasons)
