"""Typed uncertainty decomposition for epistemic, measurement and model risk.

The existing scalar uncertainty gate remains a conservative downstream policy.
This module preserves the components that a scalar max would otherwise erase.
It does not assign probabilistic meaning to incomparable uncertainty sources.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True, slots=True)
class UncertaintyVector:
    aleatoric: float = 0.0
    measurement: float = 0.0
    sampling: float = 0.0
    parameter: float = 0.0
    model: float = 0.0
    structural: float = 0.0
    state: float = 0.0
    data_generating_process: float = 0.0
    transport: float = 0.0
    adversarial: float = 0.0
    source_dependence: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.aleatoric,
            self.measurement,
            self.sampling,
            self.parameter,
            self.model,
            self.structural,
            self.state,
            self.data_generating_process,
            self.transport,
            self.adversarial,
            self.source_dependence,
        )
        if any(not isfinite(value) or not 0 <= value <= 1 for value in values):
            raise ValueError("all uncertainty components must be finite and in [0,1]")

    @property
    def epistemic(self) -> float:
        return max(self.measurement, self.parameter, self.model, self.structural, self.state, self.data_generating_process, self.transport, self.adversarial, self.source_dependence)

    @property
    def maximum(self) -> float:
        return max(self.aleatoric, self.epistemic, self.sampling)

    def conservative_merge(self, *others: "UncertaintyVector") -> "UncertaintyVector":
        vectors = (self, *others)
        fields = tuple(self.__dataclass_fields__)
        return UncertaintyVector(**{field: max(getattr(vector, field) for vector in vectors) for field in fields})

    def dominant_components(self, threshold: float = 0.75) -> tuple[str, ...]:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be in [0,1]")
        return tuple(field for field in self.__dataclass_fields__ if getattr(self, field) >= threshold)


@dataclass(frozen=True, slots=True)
class UncertaintyPropagation:
    source_refs: tuple[str, ...]
    components: UncertaintyVector
    method: str
    assumptions: tuple[str, ...]

    @property
    def abstention_required(self) -> bool:
        return bool(self.components.dominant_components())


def propagate_uncertainty(vectors: Sequence[UncertaintyVector], *, source_refs: Sequence[str] = (), method: str = "componentwise-conservative-max") -> UncertaintyPropagation:
    if not vectors:
        raise ValueError("at least one uncertainty vector is required")
    merged = vectors[0].conservative_merge(*vectors[1:])
    return UncertaintyPropagation(tuple(source_refs), merged, method, ("components are not assumed independent", "scalar downstream gates may use maximum conservatively", "no probabilistic combination is implied"))


__all__ = ["UncertaintyPropagation", "UncertaintyVector", "propagate_uncertainty"]
