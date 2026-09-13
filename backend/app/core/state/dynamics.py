"""Domain-agnostic dynamic-system metrics for CeutIA.

These primitives describe how an observed or estimated state changes over time.
They do not infer causality, forecast future outcomes, or assign semantic
meaning to a variable without domain-specific metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from ..errors import ContractViolation, TemporalViolation
from .trajectory import StateSnapshot, StateTrajectory


@dataclass(frozen=True, slots=True)
class VariableRate:
    variable: str
    delta: float
    elapsed_seconds: float
    rate: float

    def __post_init__(self) -> None:
        if not self.variable:
            raise ContractViolation("variable must not be empty")
        if self.elapsed_seconds <= 0 or not isfinite(self.elapsed_seconds):
            raise TemporalViolation("elapsed_seconds must be finite and positive")
        if not isfinite(self.delta) or not isfinite(self.rate):
            raise ContractViolation("delta and rate must be finite")


@dataclass(frozen=True, slots=True)
class RecoveryEpisode:
    baseline_state_id: str
    perturbation_state_id: str
    recovery_state_id: str
    displacement: float
    recovery_fraction: float
    recovery_seconds: float

    def __post_init__(self) -> None:
        if len({self.baseline_state_id, self.perturbation_state_id, self.recovery_state_id}) != 3:
            raise ContractViolation("recovery episode requires three distinct states")
        for name, value in (("displacement", self.displacement), ("recovery_fraction", self.recovery_fraction), ("recovery_seconds", self.recovery_seconds)):
            if not isfinite(value):
                raise ContractViolation(f"{name} must be finite")
        if self.recovery_seconds <= 0:
            raise TemporalViolation("recovery_seconds must be positive")


def _value(snapshot: StateSnapshot, variable: str) -> float | None:
    for domain in snapshot.state.domains:
        for item in domain.variables:
            if item.variable == variable:
                return float(item.value)
    return None


def trajectory_rates(trajectory: StateTrajectory, variable: str) -> tuple[VariableRate, ...]:
    """Calculate first temporal derivative between adjacent state snapshots."""
    if not variable:
        raise ContractViolation("variable must not be empty")
    result: list[VariableRate] = []
    snapshots = trajectory.snapshots
    for previous, current in zip(snapshots, snapshots[1:]):
        previous_value = _value(previous, variable)
        current_value = _value(current, variable)
        if previous_value is None or current_value is None:
            continue
        elapsed = (current.state.as_of - previous.state.as_of).total_seconds()
        if elapsed <= 0:
            raise TemporalViolation("trajectory must be strictly forward")
        delta = current_value - previous_value
        result.append(VariableRate(variable, delta, elapsed, delta / elapsed))
    return tuple(result)


def recovery_episode(
    baseline: StateSnapshot,
    perturbation: StateSnapshot,
    recovery: StateSnapshot,
    variable: str,
) -> RecoveryEpisode:
    """Quantify displacement and subsequent recovery without attributing cause."""
    if not (baseline.state.as_of < perturbation.state.as_of < recovery.state.as_of):
        raise TemporalViolation("recovery states must be strictly ordered")
    baseline_value = _value(baseline, variable)
    perturbation_value = _value(perturbation, variable)
    recovery_value = _value(recovery, variable)
    if baseline_value is None or perturbation_value is None or recovery_value is None:
        raise ContractViolation("variable must exist in all recovery states")
    displacement = perturbation_value - baseline_value
    residual = recovery_value - baseline_value
    if displacement == 0.0:
        raise ContractViolation("perturbation must displace the variable")
    recovery_fraction = 1.0 - (residual / displacement)
    recovery_seconds = (recovery.state.as_of - perturbation.state.as_of).total_seconds()
    return RecoveryEpisode(
        baseline_state_id=baseline.state.state_id,
        perturbation_state_id=perturbation.state.state_id,
        recovery_state_id=recovery.state.state_id,
        displacement=displacement,
        recovery_fraction=recovery_fraction,
        recovery_seconds=recovery_seconds,
    )
