"""State-space resilience quantities with explicit mathematical semantics.

These measures are descriptive unless a model supplies the relevant dynamics.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class ReserveState:
    capacity: float
    load: float
    perturbation: float = 0.0

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in (self.capacity, self.load, self.perturbation)):
            raise ValueError("reserve quantities must be finite")

    @property
    def margin(self) -> float:
        return self.capacity - self.load - self.perturbation

    @property
    def utilization(self) -> float:
        if self.capacity == 0:
            return float("inf") if self.load + self.perturbation > 0 else 0.0
        return (self.load + self.perturbation) / self.capacity


@dataclass(frozen=True, slots=True)
class RecoveryMetrics:
    baseline: float
    minimum: float
    final: float
    displacement: float
    recovered: float
    recovery_fraction: float
    recovery_time: float | None


class ResilienceMath:
    @staticmethod
    def recovery(
        *,
        baseline: float,
        minimum: float,
        final: float,
        recovery_time: float | None = None,
    ) -> RecoveryMetrics:
        if not all(isfinite(value) for value in (baseline, minimum, final)):
            raise ValueError("state values must be finite")
        if recovery_time is not None and (not isfinite(recovery_time) or recovery_time < 0):
            raise ValueError("recovery_time must be finite and non-negative")
        displacement = abs(baseline - minimum)
        recovered = abs(final - minimum)
        fraction = 1.0 if displacement == 0 and final == baseline else (1.0 - abs(final - baseline) / displacement if displacement else 0.0)
        return RecoveryMetrics(
            baseline=baseline,
            minimum=minimum,
            final=final,
            displacement=displacement,
            recovered=recovered,
            recovery_fraction=max(-1.0, min(1.0, fraction)),
            recovery_time=recovery_time,
        )

    @staticmethod
    def finite_difference(values: tuple[float, ...], times: tuple[float, ...]) -> tuple[float, ...]:
        if len(values) != len(times) or len(values) < 2:
            raise ValueError("values and times require equal length >= 2")
        rates: list[float] = []
        for previous, current, previous_time, current_time in zip(values, values[1:], times, times[1:]):
            dt = current_time - previous_time
            if not isfinite(dt) or dt <= 0:
                raise ValueError("times must be strictly increasing")
            rates.append((current - previous) / dt)
        return tuple(rates)

    @staticmethod
    def distance_to_linear_boundary(state: tuple[float, ...], normal: tuple[float, ...], threshold: float) -> float:
        """Signed Euclidean distance to n·x=threshold, requiring nonzero normal."""
        if len(state) != len(normal) or not state:
            raise ValueError("state and normal must have equal nonzero length")
        norm_squared = sum(value * value for value in normal)
        if norm_squared == 0:
            raise ValueError("normal must be nonzero")
        residual = sum(n * x for n, x in zip(normal, state)) - threshold
        return -residual / norm_squared ** 0.5
