"""Explicit uncertainty decomposition for CeutIA.

The aggregator never assumes independent uncertainty contributions unless the
caller explicitly declares independence. Dependent contributions are retained
as a joint component instead of being combined as if independent.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True, slots=True)
class UncertaintyComponent:
    name: str
    value: float
    kind: str
    independent_group: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.kind or not isfinite(self.value) or self.value < 0:
            raise ValueError("invalid uncertainty component")


@dataclass(frozen=True, slots=True)
class AggregatedUncertainty:
    total: float
    components: tuple[UncertaintyComponent, ...]
    method: str
    dependent_groups: tuple[str, ...]


class UncertaintyAggregator:
    """Conservative variance-style aggregation with explicit dependency groups."""

    def combine(self, components: tuple[UncertaintyComponent, ...]) -> AggregatedUncertainty:
        if not components:
            raise ValueError("components must not be empty")
        independent = [item for item in components if item.independent_group is None]
        grouped: dict[str, list[UncertaintyComponent]] = {}
        for item in components:
            if item.independent_group is not None:
                grouped.setdefault(item.independent_group, []).append(item)

        variance = sum(item.value ** 2 for item in independent)
        # Within a declared dependency group, use the conservative sum rather
        # than pretending covariance is zero.
        for group in grouped.values():
            variance += sum(item.value for item in group) ** 2
        return AggregatedUncertainty(
            total=sqrt(variance),
            components=components,
            method="quadrature_independent_plus_conservative_dependent_groups",
            dependent_groups=tuple(sorted(grouped)),
        )

    @staticmethod
    def covariance_required(components: tuple[UncertaintyComponent, ...]) -> tuple[tuple[str, str], ...]:
        grouped: dict[str, list[str]] = {}
        for item in components:
            if item.independent_group is not None:
                grouped.setdefault(item.independent_group, []).append(item.name)
        pairs: list[tuple[str, str]] = []
        for names in grouped.values():
            for index, left in enumerate(names):
                for right in names[index + 1:]:
                    pairs.append((left, right))
        return tuple(pairs)
