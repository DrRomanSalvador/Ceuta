"""Domain-neutral dynamics and regime representation."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class DynamicSignature:
    rate: float | None
    acceleration: float | None
    recovery_time: float | None
    variance: float | None
    autocorrelation: float | None
    distance_to_boundary: float | None
    regime: str | None = None

@dataclass(frozen=True, slots=True)
class TransitionEvent:
    from_state_id: str
    to_state_id: str
    perturbation_id: str | None = None
    feedback_ids: tuple[str, ...] = ()
    nonlinear: bool = False
    def __post_init__(self):
        if not self.from_state_id or not self.to_state_id: raise ContractViolation("transition states required")

@dataclass(frozen=True, slots=True)
class DynamicsSnapshot:
    signature: DynamicSignature
    transitions: tuple[TransitionEvent, ...]
    warning_flags: tuple[str, ...] = ()
