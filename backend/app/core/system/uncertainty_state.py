"""Uncertainty carried with every integrated system state.

Components remain separate because they are not interchangeable probability
quantities. Downstream conservative policy may aggregate them, but the system
retains their provenance and dominant source.
"""
from __future__ import annotations

from dataclasses import dataclass, fields

from ..errors import ContractViolation


@dataclass(frozen=True, slots=True)
class UncertaintyState:
    measurement: float = 0.0
    process: float = 0.0
    parameter: float = 0.0
    structural: float = 0.0
    selection: float = 0.0
    dependence: float = 0.0
    aleatoric: float = 0.0
    state: float = 0.0
    model: float = 0.0
    data_generating_process: float = 0.0
    transport: float = 0.0
    adversarial: float = 0.0
    source_dependence: float = 0.0

    def __post_init__(self) -> None:
        values = tuple(getattr(self, item.name) for item in fields(self))
        if any(x < 0 or x > 1 for x in values):
            raise ContractViolation("uncertainty components must be in [0,1]")

    @property
    def total_upper_bound(self) -> float:
        return sum(getattr(self, item.name) for item in fields(self))

    @property
    def conservative_upper_bound(self) -> float:
        return max(getattr(self, item.name) for item in fields(self))

    def as_mapping(self) -> dict[str, float]:
        return {item.name: getattr(self, item.name) for item in fields(self)}

    def dominant_components(self, threshold: float = 0.75) -> tuple[str, ...]:
        if not 0 <= threshold <= 1:
            raise ContractViolation("uncertainty threshold must be in [0,1]")
        return tuple(item.name for item in fields(self) if getattr(self, item.name) >= threshold)

    def merge_conservative(self, *others: "UncertaintyState") -> "UncertaintyState":
        states = (self, *others)
        return UncertaintyState(**{item.name: max(getattr(state, item.name) for state in states) for item in fields(self)})
