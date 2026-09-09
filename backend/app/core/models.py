# ---------------------------------------------------------------------------
# CeutIA — Multidimensional territorial state
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TerritorialState:
    """
    Multidimensional state of a territorial system.

    The model deliberately avoids collapsing heterogeneous dimensions into
    a single opaque risk score.

    Each dimension remains separately observable and auditable.
    """

    timestamp: datetime
    units: tuple[str, ...]
    variables: Mapping[str, tuple[float, ...]]
    area_km2: float | None = None
    adjacency_matrix: tuple[tuple[float, ...], ...] | None = None
    travel_time_matrix: tuple[tuple[float, ...], ...] | None = None
    uncertainty: Mapping[str, Uncertainty] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ModelInputError(
                "TerritorialState timestamp must be timezone-aware."
            )

        if not self.units:
            raise ModelInputError("TerritorialState requires territorial units.")

        if len(set(self.units)) != len(self.units):
            raise ModelInputError("Territorial units must be unique.")

        n = len(self.units)

        for variable, values in self.variables.items():
            if len(values) != n:
                raise ModelInputError(
                    f"Variable {variable!r} must contain one value per "
                    "territorial unit."
                )

            for index, value in enumerate(values):
                _finite(
                    value,
                    f"variables[{variable!r}][{index}]",
                )

        if self.area_km2 is not None:
            _positive(self.area_km2, "area_km2")

        if self.adjacency_matrix is not None:
            _validate_square_matrix(
                self.adjacency_matrix,
                n,
                "adjacency_matrix",
            )

        if self.travel_time_matrix is not None:
            _validate_square_matrix(
                self.travel_time_matrix,
                n,
                "travel_time_matrix",
            )

    def vector(self, variable: str) -> np.ndarray:
        """Return a variable as a numerical vector."""

        if variable not in self.variables:
            raise ModelInputError(
                f"Unknown territorial variable: {variable!r}"
            )

        return np.asarray(self.variables[variable], dtype=float)

    def mean(self, variable: str) -> float:
        return float(np.mean(self.vector(variable)))

    def maximum(self, variable: str) -> float:
        return float(np.max(self.vector(variable)))

    def minimum(self, variable: str) -> float:
        return float(np.min(self.vector(variable)))


def _validate_square_matrix(
    matrix: Sequence[Sequence[float]],
    size: int,
    name: str,
) -> None:
    array = np.asarray(matrix, dtype=float)

    if array.shape != (size, size):
        raise ModelInputError(
            f"{name} must have shape ({size}, {size})."
        )

    if not np.all(np.isfinite(array)):
        raise ModelInputError(
            f"{name} must contain only finite values."
        )


@dataclass(frozen=True, slots=True)
class TerritorialTransition:
    """
    Change between two territorial states.

    Captures state change without assigning causality.
    """

    previous: TerritorialState
    current: TerritorialState

    def __post_init__(self) -> None:
        if self.previous.units != self.current.units:
            raise ModelInputError(
                "Territorial states must use the same territorial units."
            )

        if self.current.timestamp <= self.previous.timestamp:
            raise ModelInputError(
                "Current state must occur after previous state."
            )

    @property
    def duration_seconds(self) -> float:
        return (
            self.current.timestamp - self.previous.timestamp
        ).total_seconds()

    def delta(self, variable: str) -> np.ndarray:
        previous = self.previous.vector(variable)
        current = self.current.vector(variable)

        return current - previous

    def rate(self, variable: str) -> np.ndarray:
        if self.duration_seconds <= 0:
            raise ModelInputError(
                "Transition duration must be positive."
            )

        return self.delta(variable) / self.duration_seconds


@dataclass(frozen=True, slots=True)
class CoupledSystemState:
    """
    System state represented as interacting territorial/subsystem nodes.

    The interaction matrix is structural. Its presence does not establish
    causality.
    """

    timestamp: datetime
    node_ids: tuple[str, ...]
    state_vector: tuple[float, ...]
    coupling_matrix: tuple[tuple[float, ...], ...]
    node_uncertainty: tuple[Uncertainty | None, ...] = ()

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ModelInputError(
                "CoupledSystemState timestamp must be timezone-aware."
            )

        n = len(self.node_ids)

        if n == 0:
            raise ModelInputError(
                "CoupledSystemState requires at least one node."
            )

        if len(set(self.node_ids)) != n:
            raise ModelInputError(
                "node_ids must be unique."
            )

        if len(self.state_vector) != n:
            raise ModelInputError(
                "state_vector and node_ids must have the same length."
            )

        for index, value in enumerate(self.state_vector):
            _finite(value, f"state_vector[{index}]")

        _validate_square_matrix(
            self.coupling_matrix,
            n,
            "coupling_matrix",
        )

        if self.node_uncertainty and len(self.node_uncertainty) != n:
            raise ModelInputError(
                "node_uncertainty must match node_ids length."
            )

    @property
    def spectral_radius(self) -> float:
        return coupling_spectral_radius(self.coupling_matrix)

    @property
    def mean_coupling(self) -> float:
        matrix = np.asarray(
            self.coupling_matrix,
            dtype=float,
        )

        if matrix.size == 0:
            return 0.0

        return float(np.mean(np.abs(matrix)))

    @property
    def maximum_coupling(self) -> float:
        matrix = np.asarray(
            self.coupling_matrix,
            dtype=float,
        )

        return float(np.max(np.abs(matrix)))


@dataclass(frozen=True, slots=True)
class SystemPressureState:
    """
    Separate representation of system pressure dimensions.

    Pressure is multidimensional and must not be reduced automatically to
    one universal 'risk score'.
    """

    demand: float
    capacity: float
    adaptive_reserve: float
    sensitivity: float
    coupling: float
    propagation: float
    social_tension: float
    information_pressure: float
    recovery_capacity: float

    def __post_init__(self) -> None:
        for name, value in (
            ("demand", self.demand),
            ("capacity", self.capacity),
            ("adaptive_reserve", self.adaptive_reserve),
            ("sensitivity", self.sensitivity),
            ("coupling", self.coupling),
            ("propagation", self.propagation),
            ("social_tension", self.social_tension),
            ("information_pressure", self.information_pressure),
            ("recovery_capacity", self.recovery_capacity),
        ):
            _nonnegative(value, name)

    @property
    def demand_capacity_ratio(self) -> float:
        if self.capacity == 0:
            if self.demand == 0:
                return 0.0
            return float("inf")

        return self.demand / self.capacity

    @property
    def reserve_fraction(self) -> float:
        if self.capacity == 0:
            return 0.0

        return min(
            max(self.adaptive_reserve / self.capacity, 0.0),
            1.0,
        )

    @property
    def systemic_susceptibility(self) -> float:
        return compound_systemic_susceptibility(
            sensitivity=self.sensitivity,
            reserve_fraction_remaining=self.reserve_fraction,
            coupling=self.coupling,
            propagation=self.propagation,
            recovery_capacity=self.recovery_capacity,
        )


@dataclass(frozen=True, slots=True)
class CascadeState:
    """
    Representation of propagation through a coupled system.

    This describes propagation structure. It does not claim that a cascade
    will occur.
    """

    active_nodes: tuple[str, ...]
    newly_activated_nodes: tuple[str, ...]
    generation: int
    branching_factor: float
    propagation_ratio: float
    cumulative_amplification: float
    threshold_breaches: int = 0

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise ModelInputError(
                "generation cannot be negative."
            )

        _nonnegative(
            self.branching_factor,
            "branching_factor",
        )

        _nonnegative(
            self.propagation_ratio,
            "propagation_ratio",
        )

        _nonnegative(
            self.cumulative_amplification,
            "cumulative_amplification",
        )

        if self.threshold_breaches < 0:
            raise ModelInputError(
                "threshold_breaches cannot be negative."
            )

    @property
    def has_propagation(self) -> bool:
        return bool(self.newly_activated_nodes)

    @property
    def supercritical_structure(self) -> bool:
        """
        Structural indicator only.

        A branching factor > 1 means that the observed propagation process
        generated more than one secondary event per event on average.

        It is not a probability of future cascade.
        """

        return self.branching_factor > 1.0


@dataclass(frozen=True, slots=True)
class SocialTensionState:
    """
    Aggregate social-tension representation.

    The model accepts observable signals rather than assigning an intrinsic
    hostility value to a nationality, ethnicity, religion, migrant status,
    neighbourhood population or other protected group.
    """

    timestamp: datetime
    hostility_signal: float
    hostility_velocity: float
    polarization: float
    disagreement_entropy: float
    incitement_exposure: float
    trust_erosion_signal: float
    uncertainty: Uncertainty | None = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ModelInputError(
                "SocialTensionState timestamp must be timezone-aware."
            )

        for name, value in (
            ("hostility_signal", self.hostility_signal),
            ("hostility_velocity", self.hostility_velocity),
            ("polarization", self.polarization),
            ("disagreement_entropy", self.disagreement_entropy),
            ("incitement_exposure", self.incitement_exposure),
            ("trust_erosion_signal", self.trust_erosion_signal),
        ):
            _nonnegative(value, name)

    @property
    def composite_signal(self) -> float:
        """
        Descriptive aggregate of observable tension dimensions.

        This is not a measure of the moral character or dangerousness of
        individuals or groups.
        """

        components = np.asarray(
            [
                self.hostility_signal,
                self.hostility_velocity,
                self.polarization,
                self.disagreement_entropy,
                self.incitement_exposure,
                self.trust_erosion_signal,
            ],
            dtype=float,
        )

        return float(np.mean(components))


@dataclass(frozen=True, slots=True)
class ResilienceState:
    """
    Dynamic resilience representation.

    Resilience is treated as a trajectory, not a binary property.
    """

    reserve_fraction: float
    recovery_capacity: float
    recovery_rate: float
    recovery_time_seconds: float | None
    redundancy: float
    bottleneck_dependence: float

    def __post_init__(self) -> None:
        for name, value in (
            ("reserve_fraction", self.reserve_fraction),
            ("recovery_capacity", self.recovery_capacity),
            ("recovery_rate", self.recovery_rate),
            ("redundancy", self.redundancy),
            ("bottleneck_dependence", self.bottleneck_dependence),
        ):
            _nonnegative(value, name)

        if self.recovery_time_seconds is not None:
            _nonnegative(
                self.recovery_time_seconds,
                "recovery_time_seconds",
            )

    @property
    def fragility_indicator(self) -> float:
        """
        Descriptive structural fragility.

        Higher bottleneck dependence and lower reserve/redundancy increase
        structural fragility.
        """

        denominator = (
            max(self.reserve_fraction, 1e-12)
            * max(self.redundancy, 1e-12)
        )

        return self.bottleneck_dependence / denominator


@dataclass(frozen=True, slots=True)
class DynamicRiskSignal:
    """
    Qualified analytical signal.

    `severity` is intentionally not represented here as a probability.
    The signal records the structural conditions that justify further
    human/validation attention.
    """

    signal_id: str
    timestamp: datetime
    scope: ModelScope
    dimensions: Mapping[str, float]
    triggers: tuple[str, ...]
    uncertainty: Mapping[str, Uncertainty]
    epistemic_status: EpistemicType = EpistemicType.DERIVED_SIGNAL
    requires_adversarial_validation: bool = True
    requires_human_interpretation: bool = True

    def __post_init__(self) -> None:
        if not self.signal_id.strip():
            raise ModelInputError(
                "signal_id cannot be empty."
            )

        if self.timestamp.tzinfo is None:
            raise ModelInputError(
                "DynamicRiskSignal timestamp must be timezone-aware."
            )

        for name, value in self.dimensions.items():
            _finite(value, f"dimensions[{name!r}]")

        if not self.triggers:
            raise ModelInputError(
                "A qualified signal requires at least one explicit trigger."
            )

        if self.epistemic_status in {
            EpistemicType.PREDICTION,
            EpistemicType.SCENARIO,
        } and not self.requires_adversarial_validation:
            raise ModelEpistemicError(
                "Predictions and scenarios cannot bypass adversarial validation."
            )


def build_system_pressure_state(
    *,
    demand: float,
    capacity: float,
    adaptive_reserve: float,
    sensitivity: float,
    coupling: float,
    propagation: float,
    social_tension: float,
    information_pressure: float,
    recovery_capacity: float,
) -> SystemPressureState:
    """
    Construct the multidimensional pressure state.

    No universal weighting is introduced here.
    """

    return SystemPressureState(
        demand=_nonnegative(demand, "demand"),
        capacity=_nonnegative(capacity, "capacity"),
        adaptive_reserve=_nonnegative(
            adaptive_reserve,
            "adaptive_reserve",
        ),
        sensitivity=_nonnegative(
            sensitivity,
            "sensitivity",
        ),
        coupling=_nonnegative(
            coupling,
            "coupling",
        ),
        propagation=_nonnegative(
            propagation,
            "propagation",
        ),
        social_tension=_nonnegative(
            social_tension,
            "social_tension",
        ),
        information_pressure=_nonnegative(
            information_pressure,
            "information_pressure",
        ),
        recovery_capacity=_nonnegative(
            recovery_capacity,
            "recovery_capacity",
        ),
    )


def detect_dynamic_pressure(
    pressure: SystemPressureState,
    *,
    demand_capacity_threshold: float = 1.0,
    reserve_threshold: float = 0.25,
    sensitivity_threshold: float = 1.0,
    propagation_threshold: float = 1.0,
    social_tension_threshold: float = 1.0,
) -> tuple[str, ...]:
    """
    Detect structural pressure conditions.

    The function produces interpretable triggers rather than a single
    opaque score.
    """

    _positive(
        demand_capacity_threshold,
        "demand_capacity_threshold",
    )
    _nonnegative(
        reserve_threshold,
        "reserve_threshold",
    )
    _positive(
        sensitivity_threshold,
        "sensitivity_threshold",
    )
    _positive(
        propagation_threshold,
        "propagation_threshold",
    )
    _positive(
        social_tension_threshold,
        "social_tension_threshold",
    )

    triggers: list[str] = []

    if pressure.demand_capacity_ratio >= demand_capacity_threshold:
        triggers.append("CAPACITY_PRESSURE")

    if pressure.reserve_fraction <= reserve_threshold:
        triggers.append("LOW_ADAPTIVE_RESERVE")

    if pressure.sensitivity >= sensitivity_threshold:
        triggers.append("HIGH_RESPONSE_SENSITIVITY")

    if pressure.propagation >= propagation_threshold:
        triggers.append("HIGH_PROPAGATION_STRUCTURE")

    if pressure.social_tension >= social_tension_threshold:
        triggers.append("ELEVATED_SOCIAL_TENSION_SIGNAL")

    if pressure.information_pressure > 0:
        triggers.append("INFORMATION_SYSTEM_PRESSURE")

    return tuple(triggers)


def build_dynamic_risk_signal(
    *,
    signal_id: str,
    timestamp: datetime,
    scope: ModelScope,
    pressure: SystemPressureState,
    additional_dimensions: Mapping[str, float] | None = None,
) -> DynamicRiskSignal | None:
    """
    Convert structural pressure into a qualified analytical signal.

    No signal is emitted when no explicit structural trigger exists.
    """

    triggers = detect_dynamic_pressure(pressure)

    if not triggers:
        return None

    dimensions: dict[str, float] = {
        "demand_capacity_ratio": pressure.demand_capacity_ratio,
        "reserve_fraction": pressure.reserve_fraction,
        "sensitivity": pressure.sensitivity,
        "coupling": pressure.coupling,
        "propagation": pressure.propagation,
        "social_tension": pressure.social_tension,
        "information_pressure": pressure.information_pressure,
        "recovery_capacity": pressure.recovery_capacity,
        "systemic_susceptibility": pressure.systemic_susceptibility,
    }

    if additional_dimensions:
        for name, value in additional_dimensions.items():
            dimensions[name] = _finite(
                value,
                f"additional_dimensions[{name!r}]",
            )

    return DynamicRiskSignal(
        signal_id=signal_id,
        timestamp=timestamp,
        scope=scope,
        dimensions=dimensions,
        triggers=triggers,
        uncertainty={},
    )


# Extend the public API without replacing the previous exports.
__all__.extend(
    [
        "TerritorialState",
        "TerritorialTransition",
        "CoupledSystemState",
        "SystemPressureState",
        "CascadeState",
        "SocialTensionState",
        "ResilienceState",
        "DynamicRiskSignal",
        "build_system_pressure_state",
        "detect_dynamic_pressure",
        "build_dynamic_risk_signal",
    ]
)
"""
CeutIA — Dynamic Systems Model Layer.

This module integrates the mathematical primitives defined in metrics.py
into dynamic system models.

Responsibilities:
- represent system state and trajectories;
- integrate load, adaptive reserve and capacity;
- represent perturbations and responses;
- model coupling, propagation and cascade susceptibility;
- represent territorial and temporal dynamics;
- represent information and social-tension signals as system variables;
- maintain explicit separation between observations, interpretations,
  hypotheses, predictions and scenarios;
- propagate uncertainty and epistemic limitations;
- produce qualified analytical signals for subsequent validation.

This module does NOT:
- ingest external data;
- establish scientific truth;
- diagnose individuals;
- predict individual criminality or dangerousness;
- perform autonomous policing or security decisions;
- determine who should be targeted;
- bypass adversarial validation;
- bypass information boundaries;
- expose private intelligence directly to PUBLIC.

Core principle:

    State != trajectory != prediction != scenario.

A system state describes what is observed at a given time.
A trajectory describes how that state evolves.
A hypothesis proposes an explanation.
A prediction specifies an expected future observation with a defined
horizon and uncertainty.
A scenario describes a conditional future under explicit assumptions.

No one of these representations may silently be converted into another.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from math import exp, isfinite
from typing import Mapping, Sequence

import numpy as np


class EpistemicType(StrEnum):
    """Epistemic status of an analytical object."""

    OBSERVATION = "observation"
    DERIVED_SIGNAL = "derived_signal"
    INTERPRETATION = "interpretation"
    HYPOTHESIS = "hypothesis"
    PREDICTION = "prediction"
    SCENARIO = "scenario"


class ModelScope(StrEnum):
    """Level at which a model operates."""

    SYSTEM = "system"
    TERRITORIAL = "territorial"
    POPULATION = "population"
    SUBSYSTEM = "subsystem"
    INDIVIDUAL_WELLBEING = "individual_wellbeing"


class SignalDirection(StrEnum):
    """Direction of change represented by a signal."""

    DECREASING = "decreasing"
    STABLE = "stable"
    INCREASING = "increasing"
    UNKNOWN = "unknown"


class ModelError(ValueError):
    """Base exception for invalid model construction or execution."""


class ModelInputError(ModelError):
    """Raised when model inputs are invalid."""


class ModelEpistemicError(ModelError):
    """Raised when epistemic categories are mixed incorrectly."""


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value):
        raise ModelInputError(f"{name} must be finite.")
    return value


def _nonnegative(value: float, name: str) -> float:
    value = _finite(value, name)
    if value < 0:
        raise ModelInputError(f"{name} must be non-negative.")
    return value


def _positive(value: float, name: str) -> float:
    value = _finite(value, name)
    if value <= 0:
        raise ModelInputError(f"{name} must be positive.")
    return value


def _same_length(
    left: Sequence[float],
    right: Sequence[float],
    *,
    names: tuple[str, str],
) -> None:
    if len(left) != len(right):
        raise ModelInputError(
            f"{names[0]} and {names[1]} must have the same length."
        )


@dataclass(frozen=True, slots=True)
class Uncertainty:
    """
    Explicit uncertainty attached to a model quantity.

    `value` is not a probability unless explicitly declared by the caller.
    `lower` and `upper` represent an interval in the same units as the value.
    """

    value: float
    lower: float | None = None
    upper: float | None = None
    confidence_level: float | None = None
    method: str | None = None

    def __post_init__(self) -> None:
        _finite(self.value, "value")

        if self.lower is not None:
            _finite(self.lower, "lower")

        if self.upper is not None:
            _finite(self.upper, "upper")

        if (
            self.lower is not None
            and self.upper is not None
            and self.lower > self.upper
        ):
            raise ModelInputError("lower cannot exceed upper.")

        if self.confidence_level is not None:
            if not 0 < self.confidence_level < 1:
                raise ModelInputError(
                    "confidence_level must be between 0 and 1."
                )


@dataclass(frozen=True, slots=True)
class SystemState:
    """
    Snapshot of the measurable/derived state of the system.

    A state is not a diagnosis, prediction or causal explanation.
    """

    timestamp: datetime
    variables: Mapping[str, float]
    uncertainty: Mapping[str, Uncertainty] = field(default_factory=dict)
    scope: ModelScope = ModelScope.SYSTEM

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ModelInputError("timestamp must be timezone-aware.")

        for name, value in self.variables.items():
            _finite(value, f"variables[{name!r}]")

        for name, uncertainty in self.uncertainty.items():
            if name not in self.variables:
                raise ModelInputError(
                    f"Uncertainty refers to unknown variable {name!r}."
                )
            if not isinstance(uncertainty, Uncertainty):
                raise ModelInputError(
                    f"Invalid uncertainty for variable {name!r}."
                )


@dataclass(frozen=True, slots=True)
class DynamicTrajectory:
    """Ordered trajectory of system states."""

    states: tuple[SystemState, ...]

    def __post_init__(self) -> None:
        if not self.states:
            raise ModelInputError("A trajectory requires at least one state.")

        timestamps = [state.timestamp for state in self.states]

        if timestamps != sorted(timestamps):
            raise ModelInputError(
                "Trajectory timestamps must be chronologically ordered."
            )

        if len(set(timestamps)) != len(timestamps):
            raise ModelInputError(
                "Trajectory timestamps must be unique."
            )

    @property
    def start(self) -> SystemState:
        return self.states[0]

    @property
    def end(self) -> SystemState:
        return self.states[-1]

    @property
    def duration_seconds(self) -> float:
        return (
            self.end.timestamp - self.start.timestamp
        ).total_seconds()


@dataclass(frozen=True, slots=True)
class Perturbation:
    """External or internal perturbation applied to a system."""

    timestamp: datetime
    variables: Mapping[str, float]
    duration_seconds: float | None = None
    source: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ModelInputError("Perturbation timestamp must be timezone-aware.")

        for name, value in self.variables.items():
            _finite(value, f"variables[{name!r}]")

        if self.duration_seconds is not None:
            _nonnegative(self.duration_seconds, "duration_seconds")


@dataclass(frozen=True, slots=True)
class Response:
    """Observed system response following a perturbation."""

    perturbation_id: str
    baseline: float
    response: float
    response_delta: float
    sensitivity: float | None
    elasticity: float | None
    amplification: float | None
    uncertainty: Uncertainty | None = None


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """
    Competing explanation for an observed system pattern.

    A hypothesis must remain distinguishable from observation and prediction.
    """

    hypothesis_id: str
    statement: str
    prior: float | None = None
    evidence_for: tuple[str, ...] = ()
    evidence_against: tuple[str, ...] = ()
    falsification_tests: tuple[str, ...] = ()
    status: str = "active"

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ModelInputError("hypothesis_id cannot be empty.")

        if not self.statement.strip():
            raise ModelInputError("statement cannot be empty.")

        if self.prior is not None and not 0 <= self.prior <= 1:
            raise ModelInputError("prior must be between 0 and 1.")

        if not self.falsification_tests:
            raise ModelEpistemicError(
                "Every operational hypothesis requires at least one "
                "explicit falsification test."
            )


@dataclass(frozen=True, slots=True)
class Prediction:
    """
    Conditional future expectation.

    A prediction must define:
    - target;
    - horizon;
    - expected value or range;
    - uncertainty;
    - evaluation criterion.
    """

    prediction_id: str
    target: str
    horizon_seconds: float
    expected_value: float
    uncertainty: Uncertainty
    evaluation_metric: str
    issued_at: datetime

    def __post_init__(self) -> None:
        if not self.prediction_id.strip():
            raise ModelInputError("prediction_id cannot be empty.")

        if not self.target.strip():
            raise ModelInputError("target cannot be empty.")

        _positive(self.horizon_seconds, "horizon_seconds")
        _finite(self.expected_value, "expected_value")

        if self.issued_at.tzinfo is None:
            raise ModelInputError("issued_at must be timezone-aware.")

        if not self.evaluation_metric.strip():
            raise ModelInputError(
                "Predictions require an explicit evaluation metric."
            )


@dataclass(frozen=True, slots=True)
class Scenario:
    """
    Conditional future configuration.

    A scenario is not a prediction and must never be represented as one.
    """

    scenario_id: str
    name: str
    assumptions: tuple[str, ...]
    expected_dynamics: Mapping[str, float]
    horizon_seconds: float

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ModelInputError("scenario_id cannot be empty.")

        if not self.name.strip():
            raise ModelInputError("name cannot be empty.")

        if not self.assumptions:
            raise ModelInputError(
                "A scenario requires explicit assumptions."
            )

        _positive(self.horizon_seconds, "horizon_seconds")

        for name, value in self.expected_dynamics.items():
            _finite(value, f"expected_dynamics[{name!r}]")


@dataclass(frozen=True, slots=True)
class DynamicSystemModel:
    """
    Generic state-space representation of a CeutIA system.

    Conceptual form:

        X(t+1) = F(X(t), U(t), E(t), Θ(t)) + ε(t)

    where:

        X = system state
        U = interventions/actions
        E = external/internal perturbations
        Θ = model parameters
        ε = unexplained variation/noise

    This representation is deliberately domain-agnostic.
    """

    model_id: str
    name: str
    scope: ModelScope
    state_variables: tuple[str, ...]
    parameters: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ModelInputError("model_id cannot be empty.")

        if not self.name.strip():
            raise ModelInputError("name cannot be empty.")

        if not self.state_variables:
            raise ModelInputError(
                "At least one state variable is required."
            )

        if len(set(self.state_variables)) != len(self.state_variables):
            raise ModelInputError(
                "state_variables must be unique."
            )

        for name, value in self.parameters.items():
            _finite(value, f"parameters[{name!r}]")

    def validate_state(self, state: SystemState) -> None:
        missing = set(self.state_variables) - set(state.variables)

        if missing:
            raise ModelInputError(
                f"State is missing variables: {sorted(missing)}."
            )

    def state_vector(self, state: SystemState) -> np.ndarray:
        self.validate_state(state)

        return np.asarray(
            [state.variables[name] for name in self.state_variables],
            dtype=float,
        )


@dataclass(frozen=True, slots=True)
class DynamicSystemAssessment:
    """
    Integrated dynamic assessment.

    The assessment keeps analytical layers separate rather than collapsing
    them into a single opaque risk score.
    """

    timestamp: datetime
    state: SystemState
    trajectory_velocity: Mapping[str, float]
    trajectory_acceleration: Mapping[str, float]
    load: float | None
    adaptive_reserve: float | None
    capacity: float | None
    sensitivity: float | None
    propagation: float | None
    cascade_susceptibility: float | None
    information_feedback: float | None
    social_tension_signal: float | None
    uncertainty: Mapping[str, Uncertainty] = field(default_factory=dict)
    observations: tuple[str, ...] = ()
    interpretations: tuple[str, ...] = ()
    hypotheses: tuple[Hypothesis, ...] = ()
    predictions: tuple[Prediction, ...] = ()
    scenarios: tuple[Scenario, ...] = ()

    @property
    def epistemic_types(self) -> tuple[EpistemicType, ...]:
        types: list[EpistemicType] = []

        if self.observations:
            types.append(EpistemicType.OBSERVATION)

        if (
            self.trajectory_velocity
            or self.trajectory_acceleration
            or self.load is not None
            or self.adaptive_reserve is not None
            or self.capacity is not None
        ):
            types.append(EpistemicType.DERIVED_SIGNAL)

        if self.interpretations:
            types.append(EpistemicType.INTERPRETATION)

        if self.hypotheses:
            types.append(EpistemicType.HYPOTHESIS)

        if self.predictions:
            types.append(EpistemicType.PREDICTION)

        if self.scenarios:
            types.append(EpistemicType.SCENARIO)

        return tuple(types)


def trajectory_velocity(
    trajectory: DynamicTrajectory,
    variable: str,
) -> float:
    """Estimate the latest temporal rate of change."""

    if len(trajectory.states) < 2:
        return 0.0

    previous = trajectory.states[-2]
    current = trajectory.states[-1]

    dt = (
        current.timestamp - previous.timestamp
    ).total_seconds()

    if dt <= 0:
        raise ModelInputError("Trajectory time interval must be positive.")

    return (
        current.variables[variable]
        - previous.variables[variable]
    ) / dt


def trajectory_acceleration(
    trajectory: DynamicTrajectory,
    variable: str,
) -> float:
    """Estimate the latest second temporal difference."""

    if len(trajectory.states) < 3:
        return 0.0

    a = trajectory.states[-3]
    b = trajectory.states[-2]
    c = trajectory.states[-1]

    dt1 = (b.timestamp - a.timestamp).total_seconds()
    dt2 = (c.timestamp - b.timestamp).total_seconds()

    if dt1 <= 0 or dt2 <= 0:
        raise ModelInputError("Trajectory intervals must be positive.")

    v1 = (b.variables[variable] - a.variables[variable]) / dt1
    v2 = (c.variables[variable] - b.variables[variable]) / dt2

    return (v2 - v1) / ((dt1 + dt2) / 2.0)


def adaptive_reserve_state(
    capacity: float,
    accumulated_load: float,
) -> float:
    """
    Compute remaining adaptive reserve.

        R = max(C - L, 0)

    This is a state quantity, not a probability of failure.
    """

    capacity = _nonnegative(capacity, "capacity")
    accumulated_load = _nonnegative(
        accumulated_load,
        "accumulated_load",
    )

    return max(capacity - accumulated_load, 0.0)


def reserve_fraction(
    reserve: float,
    capacity: float,
) -> float:
    """Normalize adaptive reserve to available capacity."""

    reserve = _nonnegative(reserve, "reserve")
    capacity = _positive(capacity, "capacity")

    return min(max(reserve / capacity, 0.0), 1.0)


def shock_response_sensitivity(
    shock: float,
    response: float,
    *,
    epsilon: float = 1e-12,
) -> float:
    """
    Local response sensitivity.

        S = Δresponse / Δshock
    """

    shock = _finite(shock, "shock")
    response = _finite(response, "response")

    if abs(shock) <= epsilon:
        raise ModelInputError(
            "Sensitivity is undefined for a zero perturbation."
        )

    return response / shock


def response_amplification(
    shock: float,
    response: float,
    *,
    epsilon: float = 1e-12,
) -> float:
    """
    Absolute amplification ratio.

        A = |Δresponse| / |Δshock|
    """

    shock = _finite(shock, "shock")
    response = _finite(response, "response")

    if abs(shock) <= epsilon:
        raise ModelInputError(
            "Amplification is undefined for a zero perturbation."
        )

    return abs(response) / abs(shock)


def coupling_spectral_radius(
    coupling_matrix: Sequence[Sequence[float]],
) -> float:
    """
    Spectral radius of the system coupling matrix.

    The spectral radius is a structural property of the interaction matrix.
    It is not, by itself, a probability of cascade or mortality.
    """

    matrix = np.asarray(coupling_matrix, dtype=float)

    if matrix.ndim != 2:
        raise ModelInputError("coupling_matrix must be two-dimensional.")

    if matrix.shape[0] != matrix.shape[1]:
        raise ModelInputError("coupling_matrix must be square.")

    if not np.all(np.isfinite(matrix)):
        raise ModelInputError(
            "coupling_matrix must contain only finite values."
        )

    eigenvalues = np.linalg.eigvals(matrix)

    if eigenvalues.size == 0:
        return 0.0

    return float(np.max(np.abs(eigenvalues)))


def branching_factor(
    offspring_counts: Sequence[float],
) -> float:
    """
    Mean secondary propagation generated by an event.

    This is descriptive unless validated against an operational outcome.
    """

    values = np.asarray(offspring_counts, dtype=float)

    if values.ndim != 1 or values.size == 0:
        raise ModelInputError(
            "offspring_counts must be a non-empty one-dimensional sequence."
        )

    if np.any(~np.isfinite(values)):
        raise ModelInputError(
            "offspring_counts must contain finite values."
        )

    if np.any(values < 0):
        raise ModelInputError(
            "offspring_counts cannot contain negative values."
        )

    return float(np.mean(values))


def compound_systemic_susceptibility(
    *,
    sensitivity: float,
    reserve_fraction_remaining: float,
    coupling: float,
    propagation: float,
    recovery_capacity: float,
) -> float:
    """
    Composite susceptibility to disproportionate system response.

    The quantity is deliberately a susceptibility index, not a probability.

    Higher sensitivity, coupling and propagation increase susceptibility.
    Greater remaining reserve and recovery capacity reduce it.

        S_c ∝ sensitivity × coupling × propagation
              / (reserve × recovery)

    No causal or predictive interpretation is permitted without validation.
    """

    sensitivity = _nonnegative(sensitivity, "sensitivity")
    reserve_fraction_remaining = _nonnegative(
        reserve_fraction_remaining,
        "reserve_fraction_remaining",
    )
    coupling = _nonnegative(coupling, "coupling")
    propagation = _nonnegative(propagation, "propagation")
    recovery_capacity = _nonnegative(
        recovery_capacity,
        "recovery_capacity",
    )

    denominator = (
        max(reserve_fraction_remaining, 1e-12)
        * max(recovery_capacity, 1e-12)
    )

    return (
        sensitivity
        * coupling
        * propagation
        / denominator
    )


def information_feedback_sensitivity(
    information_change: float,
    system_change: float,
    *,
    epsilon: float = 1e-12,
) -> float:
    """
    Estimate system response associated with an information change.

        F_I = Δsystem / Δinformation

    This does not establish that information caused the system change.
    """

    information_change = _finite(
        information_change,
        "information_change",
    )
    system_change = _finite(system_change, "system_change")

    if abs(information_change) <= epsilon:
        raise ModelInputError(
            "Information feedback sensitivity is undefined for "
            "zero information change."
        )

    return system_change / information_change


def sigmoid_response(
    stimulus: float,
    midpoint: float,
    steepness: float,
    maximum_response: float = 1.0,
) -> float:
    """
    Generic nonlinear threshold-response function.

        y = M / (1 + exp(-k(x-x0)))

    It describes a possible response shape; it does not establish that
    the real system follows this function.
    """

    stimulus = _finite(stimulus, "stimulus")
    midpoint = _finite(midpoint, "midpoint")
    steepness = _finite(steepness, "steepness")
    maximum_response = _nonnegative(
        maximum_response,
        "maximum_response",
    )

    exponent = -steepness * (stimulus - midpoint)

    # Numerically stable logistic evaluation.
    if exponent >= 0:
        z = exp(-exponent)
        denominator = 1.0 + z
        return maximum_response / denominator

    z = exp(exponent)
    return maximum_response * z / (1.0 + z)


def validate_epistemic_separation(
    *,
    observation: str | None = None,
    interpretation: str | None = None,
    hypothesis: Hypothesis | None = None,
    prediction: Prediction | None = None,
    scenario: Scenario | None = None,
) -> None:
    """
    Prevent silent epistemic conversion.

    The function does not prohibit using different epistemic objects
    together. It ensures that each remains explicitly represented.
    """

    if hypothesis is not None and not hypothesis.falsification_tests:
        raise ModelEpistemicError(
            "Hypotheses require explicit falsification tests."
        )

    if prediction is not None:
        if prediction.horizon_seconds <= 0:
            raise ModelEpistemicError(
                "Predictions require a positive evaluation horizon."
            )

    if scenario is not None and not scenario.assumptions:
        raise ModelEpistemicError(
            "Scenarios require explicit assumptions."
        )

    if (
        observation is not None
        and interpretation is not None
        and observation.strip() == interpretation.strip()
    ):
        raise ModelEpistemicError(
            "Observation and interpretation must not be silently "
            "collapsed into the same epistemic statement."
        )


def build_dynamic_assessment(
    *,
    state: SystemState,
    trajectory: DynamicTrajectory,
    variables: Sequence[str],
    load: float | None = None,
    adaptive_reserve: float | None = None,
    capacity: float | None = None,
    sensitivity: float | None = None,
    propagation: float | None = None,
    cascade_susceptibility: float | None = None,
    information_feedback: float | None = None,
    social_tension_signal: float | None = None,
    observations: Sequence[str] = (),
    interpretations: Sequence[str] = (),
    hypotheses: Sequence[Hypothesis] = (),
    predictions: Sequence[Prediction] = (),
    scenarios: Sequence[Scenario] = (),
) -> DynamicSystemAssessment:
    """
    Construct an integrated dynamic assessment without collapsing
    different epistemic layers into one score.
    """

    if trajectory.end.timestamp != state.timestamp:
        raise ModelInputError(
            "Assessment state must correspond to the trajectory endpoint."
        )

    velocity = {
        variable: trajectory_velocity(trajectory, variable)
        for variable in variables
        if variable in state.variables
    }

    acceleration = {
        variable: trajectory_acceleration(trajectory, variable)
        for variable in variables
        if variable in state.variables
    }

    for name, value in (
        ("load", load),
        ("adaptive_reserve", adaptive_reserve),
        ("capacity", capacity),
        ("sensitivity", sensitivity),
        ("propagation", propagation),
        ("cascade_susceptibility", cascade_susceptibility),
        ("information_feedback", information_feedback),
        ("social_tension_signal", social_tension_signal),
    ):
        if value is not None:
            _finite(value, name)

    for hypothesis in hypotheses:
        validate_epistemic_separation(hypothesis=hypothesis)

    for prediction in predictions:
        validate_epistemic_separation(prediction=prediction)

    for scenario in scenarios:
        validate_epistemic_separation(scenario=scenario)

    return DynamicSystemAssessment(
        timestamp=state.timestamp,
        state=state,
        trajectory_velocity=velocity,
        trajectory_acceleration=acceleration,
        load=load,
        adaptive_reserve=adaptive_reserve,
        capacity=capacity,
        sensitivity=sensitivity,
        propagation=propagation,
        cascade_susceptibility=cascade_susceptibility,
        information_feedback=information_feedback,
        social_tension_signal=social_tension_signal,
        observations=tuple(observations),
        interpretations=tuple(interpretations),
        hypotheses=tuple(hypotheses),
        predictions=tuple(predictions),
        scenarios=tuple(scenarios),
    )


DYNAMIC_SYSTEM_MODEL_INVARIANTS: tuple[str, ...] = (
    "State is not trajectory.",
    "Trajectory is not prediction.",
    "Prediction is not scenario.",
    "Observation is not interpretation.",
    "Correlation is not causation.",
    "Temporal precedence is not causal proof.",
    "A metric is not a diagnosis.",
    "A susceptibility index is not a probability.",
    "A probability is not valid without calibration and defined outcome/horizon.",
    "A model output is not operationally valid without appropriate validation.",
    "Small geographic area does not imply high coupling by itself.",
    "Coupling must be represented by measurable interaction structure.",
    "Social hostility must be represented through observable aggregate signals, "
    "not intrinsic dangerousness assigned to protected groups.",
    "Migration status or nationality must never be used as a proxy for "
    "individual criminality or dangerousness.",
    "Individual wellbeing signals must remain distinct from population-level "
    "system intelligence.",
    "Contradictory evidence must be preserved rather than silently resolved.",
    "CeutIA must not make autonomous security decisions.",
    "Human interpretation remains mandatory before operational escalation.",
    "Private intelligence cannot become public through implicit serialization.",
    "No mathematical formula establishes truth without empirical validation.",
    "No single composite score may conceal its component dimensions and uncertainty.",
    "All operational predictions require a defined target, horizon and "
    "evaluation criterion.",
    "Every operational hypothesis requires an explicit falsification route.",
    "System feedback created by CeutIA must be treated as part of the "
    "system dynamics and monitored for self-confirmation."
)


__all__ = [
    "EpistemicType",
    "ModelScope",
    "SignalDirection",
    "ModelError",
    "ModelInputError",
    "ModelEpistemicError",
    "Uncertainty",
    "SystemState",
    "DynamicTrajectory",
    "Perturbation",
    "Response",
    "Hypothesis",
    "Prediction",
    "Scenario",
    "DynamicSystemModel",
    "DynamicSystemAssessment",
    "trajectory_velocity",
    "trajectory_acceleration",
    "adaptive_reserve_state",
    "reserve_fraction",
    "shock_response_sensitivity",
    "response_amplification",
    "coupling_spectral_radius",
    "branching_factor",
    "compound_systemic_susceptibility",
    "information_feedback_sensitivity",
    "sigmoid_response",
    "validate_epistemic_separation",
    "build_dynamic_assessment",
    "DYNAMIC_SYSTEM_MODEL_INVARIANTS",
]
"""
CeutIA — Modelos dinámicos de sistemas complejos.

Este módulo integra las magnitudes matemáticas calculadas por metrics.py
en modelos dinámicos, territoriales, de capacidad, propagación, resiliencia,
información, hipótesis y riesgo sistémico.

PRINCIPIO ARQUITECTÓNICO
========================

metrics.py
    ↓
    magnitudes matemáticas
    ↓
models.py
    ↓
    estado + trayectoria + interacciones + hipótesis + escenarios
    ↓
adversarial_validation.py
    ↓
    refutación / robustez / validación
    ↓
information_boundary.py
    ↓
    PUBLIC / PRIVATE / INTERNAL

Este módulo NO:

- ingiere datos;
- ejecuta decisiones de seguridad;
- realiza vigilancia individual;
- predice criminalidad individual;
- asigna peligrosidad a nacionalidades, grupos o colectivos;
- convierte migración en criminalidad;
- convierte hostilidad agregada en un atributo de personas;
- genera automáticamente actuaciones de autoridades.

El objetivo es modelar el comportamiento de un sistema complejo.

La unidad fundamental no es el número aislado.

Es:

    estado
    trayectoria
    velocidad
    aceleración
    carga
    reserva
    capacidad
    acoplamiento
    sensibilidad
    propagación
    umbral
    recuperación
    información
    interacción

La arquitectura de riesgo de CeutIA es sistémica:

    R(t) = F(
        estado,
        trayectoria,
        carga,
        reserva,
        capacidad,
        acoplamiento,
        sensibilidad,
        propagación,
        umbrales,
        información,
        señales sociales,
        recuperación,
        incertidumbre
    )

R(t) NO significa automáticamente:

    P(persona peligrosa)

ni:

    P(grupo peligroso)

ni:

    P(delito individual)

Puede representar únicamente una condición de fragilidad,
tensión, presión, transición o susceptibilidad del sistema.

PRINCIPIO EPISTEMOLÓGICO
========================

Una conclusión que sobrevive a una prueba de refutación no se convierte
por ello en verdadera.

La robustez frente a una perturbación concreta tampoco equivale a verdad.

CeutIA conserva separadas:

    observación
    cálculo
    inferencia
    hipótesis
    predicción
    escenario
    decisión

Una predicción cuantitativa requiere:

    outcome definido
    horizonte definido
    datos apropiados
    validación
    calibración
    evaluación temporal/external
    comparación posterior con el outcome real

Sin ello, el sistema puede producir una señal de susceptibilidad,
presión o fragilidad, pero no una probabilidad operacional de daño.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import exp, isfinite, sqrt
from typing import Final, Mapping, Sequence

import numpy as np


# ============================================================================
# ENUMERACIONES
# ============================================================================


class ModelDomain(StrEnum):
    """Dominios de modelización."""

    GENERAL = "general"
    TERRITORIAL = "territorial"
    HEALTH = "health"
    EPIDEMIOLOGY = "epidemiology"
    CAPACITY = "capacity"
    QUEUEING = "queueing"
    NETWORK = "network"
    SOCIAL = "social"
    INFORMATION = "information"
    ENVIRONMENT = "environment"
    CLIMATE = "climate"
    MIGRATION = "migration"
    SECURITY = "security"
    STRATEGIC = "strategic"
    RESILIENCE = "resilience"
    SYSTEM_DYNAMICS = "system_dynamics"
    SCENARIO = "scenario"


class EpistemicStatus(StrEnum):
    """Estado epistemológico de una salida."""

    OBSERVED = "observed"
    CALCULATED = "calculated"
    INFERRED = "inferred"
    HYPOTHESIS = "hypothesis"
    PREDICTION = "prediction"
    SCENARIO = "scenario"
    INDETERMINATE = "indeterminate"


class ModelStatus(StrEnum):
    """Estado de validación del modelo."""

    EXPLORATORY = "exploratory"
    RETROSPECTIVELY_VALIDATED = "retrospectively_validated"
    TEMPORALLY_VALIDATED = "temporally_validated"
    EXTERNALLY_VALIDATED = "externally_validated"
    PROSPECTIVELY_VALIDATED = "prospectively_validated"
    BLOCKED = "blocked"


class RiskTarget(StrEnum):
    """
    Nivel al que puede referirse un resultado.

    Los niveles individual y grupal se incluyen para poder bloquear
    explícitamente usos no permitidos.
    """

    SYSTEM = "system"
    TERRITORIAL_UNIT = "territorial_unit"
    POPULATION = "population"
    EVENT = "event"
    INDIVIDUAL = "individual"
    GROUP = "group"


class ModelOutputType(StrEnum):
    """Tipo de salida."""

    STATE = "state"
    TRAJECTORY = "trajectory"
    PRESSURE = "pressure"
    FRAGILITY = "fragility"
    SUSCEPTIBILITY = "susceptibility"
    CAPACITY = "capacity"
    PROPAGATION = "propagation"
    RECOVERY = "recovery"
    HYPOTHESIS = "hypothesis"
    SCENARIO = "scenario"
    PREDICTION = "prediction"


# ============================================================================
# EXCEPCIONES
# ============================================================================


class ModelError(ValueError):
    """Error base de modelización."""


class ModelInputError(ModelError):
    """Entrada incompatible o fuera de dominio."""


class ModelValidationError(ModelError):
    """Modelo no suficientemente validado."""


class ModelSafetyError(ModelError):
    """Uso del modelo incompatible con las invariantes de CeutIA."""


class ModelEpistemicError(ModelError):
    """Mezcla incorrecta de categorías epistemológicas."""


# ============================================================================
# UTILIDADES NUMÉRICAS
# ============================================================================


_EPS: Final[float] = 1e-12


def _vector(
    values: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    arr = np.asarray(values, dtype=float)

    if arr.ndim != 1:
        raise ModelInputError(
            f"{name} debe ser un vector unidimensional."
        )

    if arr.size == 0:
        raise ModelInputError(
            f"{name} no puede estar vacío."
        )

    if not np.all(np.isfinite(arr)):
        raise ModelInputError(
            f"{name} contiene valores no finitos."
        )

    return arr


def _matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    arr = np.asarray(values, dtype=float)

    if arr.ndim != 2:
        raise ModelInputError(
            f"{name} debe ser una matriz bidimensional."
        )

    if arr.size == 0:
        raise ModelInputError(
            f"{name} no puede estar vacía."
        )

    if not np.all(np.isfinite(arr)):
        raise ModelInputError(
            f"{name} contiene valores no finitos."
        )

    return arr


def _same_shape(
    left: np.ndarray,
    right: np.ndarray,
    *,
    names: str = "arrays",
) -> None:
    if left.shape != right.shape:
        raise ModelInputError(
            f"{names} deben tener la misma forma."
        )


def _bounded(
    value: float,
    *,
    lower: float = 0.0,
    upper: float = 1.0,
) -> float:
    if not isfinite(float(value)):
        raise ModelInputError(
            "El valor debe ser finito."
        )

    if lower > upper:
        raise ModelInputError(
            "Límites inválidos."
        )

    return float(
        max(lower, min(upper, value))
    )


def _safe_ratio(
    numerator: float,
    denominator: float,
) -> float:
    if not isfinite(float(numerator)):
        raise ModelInputError(
            "Numerador no finito."
        )

    if not isfinite(float(denominator)):
        raise ModelInputError(
            "Denominador no finito."
        )

    if abs(denominator) <= _EPS:
        if abs(numerator) <= _EPS:
            return 0.0

        return float(
            np.sign(numerator) * np.inf
        )

    return float(numerator / denominator)


# ============================================================================
# ESTADO DINÁMICO
# ============================================================================


@dataclass(frozen=True, slots=True)
class DynamicState:
    """
    Estado instantáneo del sistema.

    Un estado no debe interpretarse sin su contexto temporal.
    """

    timestamp: float

    values: Mapping[str, float]

    uncertainty: Mapping[str, float] = field(
        default_factory=dict
    )

    spatial_unit: str | None = None

    observed: bool = True

    def validate(self) -> None:
        if not isfinite(self.timestamp):
            raise ModelInputError(
                "timestamp debe ser finito."
            )

        for name, value in self.values.items():

            if not isfinite(float(value)):
                raise ModelInputError(
                    f"Estado no finito: {name}."
                )

        for name, value in self.uncertainty.items():

            if not 0.0 <= float(value) <= 1.0:
                raise ModelInputError(
                    f"Incertidumbre inválida para {name}."
                )


@dataclass(frozen=True, slots=True)
class DynamicTrajectory:
    """
    Trayectoria temporal de un estado.

    Representa explícitamente:

        X(t)
        dX/dt
        d²X/dt²
    """

    timestamps: tuple[float, ...]
    values: tuple[float, ...]

    velocity: tuple[float, ...]
    acceleration: tuple[float, ...]

    def validate(self) -> None:
        if len(self.timestamps) != len(self.values):
            raise ModelInputError(
                "timestamps y values deben tener la misma longitud."
            )

        if len(self.timestamps) < 2:
            raise ModelInputError(
                "Una trayectoria requiere al menos dos observaciones."
            )

        if len(self.velocity) != len(self.values):
            raise ModelInputError(
                "velocity debe tener la misma longitud que values."
            )

        if len(self.acceleration) != len(self.values):
            raise ModelInputError(
                "acceleration debe tener la misma longitud que values."
            )

        time = _vector(
            self.timestamps,
            name="timestamps",
        )

        if np.any(np.diff(time) <= 0):
            raise ModelInputError(
                "Los timestamps deben ser estrictamente crecientes."
            )


def build_dynamic_trajectory(
    timestamps: Sequence[float],
    values: Sequence[float],
) -> DynamicTrajectory:
    """
    Construye una trayectoria con velocidad y aceleración.

    Las derivadas se calculan respetando el espaciado temporal real.
    """

    time = _vector(
        timestamps,
        name="timestamps",
    )

    value = _vector(
        values,
        name="values",
    )

    _same_shape(
        time,
        value,
        names="timestamps y values",
    )

    if time.size < 2:
        raise ModelInputError(
            "Se requieren al menos dos observaciones."
        )

    if np.any(np.diff(time) <= 0):
        raise ModelInputError(
            "Los timestamps deben ser estrictamente crecientes."
        )

    velocity = np.gradient(
        value,
        time,
    )

    acceleration = np.gradient(
        velocity,
        time,
    )

    trajectory = DynamicTrajectory(
        timestamps=tuple(float(x) for x in time),
        values=tuple(float(x) for x in value),
        velocity=tuple(float(x) for x in velocity),
        acceleration=tuple(float(x) for x in acceleration),
    )

    trajectory.validate()

    return trajectory


# ============================================================================
# CARGA Y RESERVA ADAPTATIVA
# ============================================================================


@dataclass(frozen=True, slots=True)
class ReserveState:
    """
    Estado de reserva adaptativa.

    reserve(t) representa capacidad disponible después de la carga acumulada.

    Conceptualmente:

        R(t+1) = R(t) + recovery(t) - load(t)
    """

    initial_reserve: float
    current_reserve: float
    cumulative_load: float
    cumulative_recovery: float

    depletion_fraction: float
    headroom: float

    def validate(self) -> None:
        if self.initial_reserve <= 0:
            raise ModelInputError(
                "initial_reserve debe ser > 0."
            )

        if self.current_reserve < 0:
            raise ModelInputError(
                "current_reserve no puede ser negativo."
            )

        if self.cumulative_load < 0:
            raise ModelInputError(
                "cumulative_load no puede ser negativo."
            )

        if self.cumulative_recovery < 0:
            raise ModelInputError(
                "cumulative_recovery no puede ser negativo."
            )

        if not 0.0 <= self.depletion_fraction <= 1.0:
            raise ModelInputError(
                "depletion_fraction debe estar en [0, 1]."
            )


def adaptive_reserve_trajectory(
    initial_reserve: float,
    load: Sequence[float],
    recovery: Sequence[float] | None = None,
) -> np.ndarray:
    """
    Evolución de la reserva adaptativa.

        R_t = max(
            0,
            R_0 + Σ(recovery_t - load_t)
        )

    La versión interna no convierte reserva negativa en un riesgo.
    Una reserva agotada significa que el modelo ha alcanzado un límite.
    """

    if initial_reserve <= 0:
        raise ModelInputError(
            "initial_reserve debe ser > 0."
        )

    load_arr = _vector(
        load,
        name="load",
    )

    if np.any(load_arr < 0):
        raise ModelInputError(
            "load no puede contener valores negativos."
        )

    if recovery is None:

        recovery_arr = np.zeros_like(
            load_arr
        )

    else:

        recovery_arr = _vector(
            recovery,
            name="recovery",
        )

        _same_shape(
            load_arr,
            recovery_arr,
            names="load y recovery",
        )

        if np.any(recovery_arr < 0):
            raise ModelInputError(
                "recovery no puede contener valores negativos."
            )

    delta = recovery_arr - load_arr

    reserve = np.empty_like(
        load_arr
    )

    current = float(initial_reserve)

    for index, change in enumerate(delta):

        current = max(
            0.0,
            current + float(change),
        )

        reserve[index] = current

    return reserve


def reserve_depletion_fraction(
    initial_reserve: float,
    current_reserve: float,
) -> float:
    if initial_reserve <= 0:
        raise ModelInputError(
            "initial_reserve debe ser > 0."
        )

    if current_reserve < 0:
        raise ModelInputError(
            "current_reserve no puede ser negativo."
        )

    return _bounded(
        1.0 - current_reserve / initial_reserve
    )


def reserve_headroom(
    current_reserve: float,
    capacity: float,
) -> float:
    """
    Reserva relativa respecto a una capacidad de referencia.
    """

    if current_reserve < 0:
        raise ModelInputError(
            "current_reserve no puede ser negativo."
        )

    if capacity <= 0:
        raise ModelInputError(
            "capacity debe ser > 0."
        )

    return _bounded(
        current_reserve / capacity
    )


# ============================================================================
# CAPACIDAD, DEMANDA Y BOTTLENECK
# ============================================================================


@dataclass(frozen=True, slots=True)
class CapacityState:
    """
    Relación entre demanda y capacidad.

        rho = λ / μ

    pero sin asumir que el sistema sea estacionario.

    Para CeutIA interesa especialmente la dinámica de rho.
    """

    demand: float
    capacity: float

    utilization: float
    excess_demand: float
    reserve_fraction: float

    saturated: bool

    def validate(self) -> None:
        if self.demand < 0:
            raise ModelInputError(
                "demand no puede ser negativa."
            )

        if self.capacity <= 0:
            raise ModelInputError(
                "capacity debe ser > 0."
            )


def capacity_state(
    demand: float,
    capacity: float,
) -> CapacityState:
    if demand < 0:
        raise ModelInputError(
            "demand no puede ser negativa."
        )

    if capacity <= 0:
        raise ModelInputError(
            "capacity debe ser > 0."
        )

    utilization = demand / capacity

    result = CapacityState(
        demand=float(demand),
        capacity=float(capacity),
        utilization=float(utilization),
        excess_demand=float(
            max(0.0, demand - capacity)
        ),
        reserve_fraction=float(
            max(0.0, (capacity - demand) / capacity)
        ),
        saturated=bool(
            utilization >= 1.0
        ),
    )

    result.validate()

    return result


def capacity_trajectory(
    demand: Sequence[float],
    capacity: Sequence[float],
) -> np.ndarray:
    demand_arr = _vector(
        demand,
        name="demand",
    )

    capacity_arr = _vector(
        capacity,
        name="capacity",
    )

    _same_shape(
        demand_arr,
        capacity_arr,
        names="demand y capacity",
    )

    if np.any(demand_arr < 0):
        raise ModelInputError(
            "demand no puede ser negativa."
        )

    if np.any(capacity_arr <= 0):
        raise ModelInputError(
            "capacity debe ser estrictamente positiva."
        )

    return demand_arr / capacity_arr


def first_bottleneck(
    demand: Sequence[float],
    capacity: Sequence[float],
) -> int | None:
    """
    Devuelve el primer instante en que la utilización alcanza 1.

    No presupone estacionariedad.
    """

    utilization = capacity_trajectory(
        demand,
        capacity,
    )

    indices = np.flatnonzero(
        utilization >= 1.0
    )

    if indices.size == 0:
        return None

    return int(indices[0])


def bottleneck_severity(
    demand: Sequence[float],
    capacity: Sequence[float],
) -> np.ndarray:
    """
    Exceso relativo de demanda:

        B(t) = max(0, D(t)/C(t) - 1)
    """

    utilization = capacity_trajectory(
        demand,
        capacity,
    )

    return np.maximum(
        utilization - 1.0,
        0.0,
    )


# ============================================================================
# ACOPLAMIENTO TERRITORIAL
# ============================================================================


@dataclass(frozen=True, slots=True)
class TerritorialState:
    """
    Estado multidimensional por unidad territorial.

    Las unidades pueden ser barrios, sectores, celdas u otras unidades
    definidas por el sistema.

    La escala debe conservarse porque los resultados pueden cambiar
    con la resolución espacial.
    """

    unit_ids: tuple[str, ...]

    demand: tuple[float, ...]
    capacity: tuple[float, ...]

    exposure: tuple[float, ...]
    reserve: tuple[float, ...]

    interaction_matrix: tuple[tuple[float, ...], ...]

    def validate(self) -> None:
        n = len(self.unit_ids)

        if n == 0:
            raise ModelInputError(
                "Debe existir al menos una unidad territorial."
            )

        arrays = (
            self.demand,
            self.capacity,
            self.exposure,
            self.reserve,
        )

        for values in arrays:

            if len(values) != n:
                raise ModelInputError(
                    "Todas las variables territoriales deben "
                    "tener una observación por unidad."
                )

        matrix = _matrix(
            self.interaction_matrix,
            name="interaction_matrix",
        )

        if matrix.shape != (n, n):
            raise ModelInputError(
                "interaction_matrix debe tener dimensión n × n."
            )

        if np.any(matrix < 0):
            raise ModelInputError(
                "Las intensidades de interacción no pueden ser negativas."
            )

        if np.any(
            _vector(
                self.capacity,
                name="capacity",
            )
            <= 0
        ):
            raise ModelInputError(
                "Toda capacidad territorial debe ser > 0."
            )


def territorial_utilization(
    demand: Sequence[float],
    capacity: Sequence[float],
) -> np.ndarray:
    return capacity_trajectory(
        demand,
        capacity,
    )


def territorial_spatial_lag(
    values: Sequence[float],
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    L_i = Σ_j W_ij X_j

    Representa presión/influencia proveniente de otras unidades.

    No implica causalidad.
    """

    x = _vector(
        values,
        name="values",
    )

    W = _matrix(
        interaction_matrix,
        name="interaction_matrix",
    )

    if W.shape != (x.size, x.size):
        raise ModelInputError(
            "La matriz de interacción debe ser n × n."
        )

    return W @ x


def normalized_interaction_matrix(
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Normalización por suma de filas.

    Conserva la estructura relativa de las conexiones.
    """

    W = _matrix(
        interaction_matrix,
        name="interaction_matrix",
    )

    row_sum = np.sum(
        W,
        axis=1,
        keepdims=True,
    )

    result = np.divide(
        W,
        row_sum,
        out=np.zeros_like(W),
        where=row_sum > _EPS,
    )

    return result


def coupling_spectral_radius(
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Radio espectral de la matriz de interacción.

    Un valor elevado puede indicar potencial de amplificación estructural,
    pero NO constituye por sí mismo una predicción de cascada.
    """

    W = _matrix(
        interaction_matrix,
        name="interaction_matrix",
    )

    if W.shape[0] != W.shape[1]:
        raise ModelInputError(
            "La matriz debe ser cuadrada."
        )

    eigenvalues = np.linalg.eigvals(
        W
    )

    return float(
        np.max(
            np.abs(eigenvalues)
        )
    )


def territorial_coupling_strength(
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    W = _matrix(
        interaction_matrix,
        name="interaction_matrix",
    )

    off_diagonal = W.copy()

    np.fill_diagonal(
        off_diagonal,
        0.0,
    )

    return float(
        np.mean(off_diagonal)
    )


# ============================================================================
# SENSIBILIDAD Y PEQUEÑOS ESTÍMULOS
# ============================================================================


def local_sensitivity(
    baseline_input: float,
    perturbed_input: float,
    baseline_output: float,
    perturbed_output: float,
) -> float:
    """
    Sensibilidad local:

        S = ΔY / ΔX
    """

    delta_x = perturbed_input - baseline_input

    if abs(delta_x) <= _EPS:
        raise ModelInputError(
            "El estímulo debe cambiar."
        )

    return float(
        (perturbed_output - baseline_output)
        / delta_x
    )


def local_elasticity(
    baseline_input: float,
    perturbed_input: float,
    baseline_output: float,
    perturbed_output: float,
) -> float:
    """
    Elasticidad:

        E = (ΔY / Y) / (ΔX / X)

    Se exige X,Y > 0.
    """

    if baseline_input <= 0:
        raise ModelInputError(
            "baseline_input debe ser > 0."
        )

    if baseline_output <= 0:
        raise ModelInputError(
            "baseline_output debe ser > 0."
        )

    relative_input = (
        perturbed_input - baseline_input
    ) / baseline_input

    relative_output = (
        perturbed_output - baseline_output
    ) / baseline_output

    if abs(relative_input) <= _EPS:
        raise ModelInputError(
            "El cambio relativo de input es demasiado pequeño."
        )

    return float(
        relative_output / relative_input
    )


def amplification_factor(
    baseline_output: float,
    perturbed_output: float,
    stimulus: float,
) -> float:
    """
    Amplificación:

        A = |ΔY| / |stimulus|

    Una amplificación elevada indica sensibilidad del sistema,
    no necesariamente daño ni causalidad.
    """

    if stimulus <= 0:
        raise ModelInputError(
            "stimulus debe ser > 0."
        )

    return float(
        abs(perturbed_output - baseline_output)
        / stimulus
    )


def regularized_transition_susceptibility(
    threshold_distance: float,
    sensitivity: float,
) -> float:
    """
    Susceptibilidad próxima a un umbral.

    En lugar de utilizar 1/d directamente, se utiliza una regularización
    que evita una singularidad numérica.

        S_T = sensitivity / (1 + d)

    donde d >= 0.

    Cuanto menor sea la distancia al umbral y mayor la sensibilidad,
    mayor será la susceptibilidad estructural.

    NO es una probabilidad.
    """

    if threshold_distance < 0:
        raise ModelInputError(
            "threshold_distance no puede ser negativa."
        )

    if sensitivity < 0:
        raise ModelInputError(
            "sensitivity no puede ser negativa."
        )

    return float(
        sensitivity
        / (1.0 + threshold_distance)
    )


# ============================================================================
# UMBRALES Y TRANSICIONES
# ============================================================================


def threshold_distance(
    state: float,
    threshold: float,
) -> float:
    """
    Distancia absoluta al umbral.
    """

    return float(
        abs(threshold - state)
    )


def threshold_margin(
    state: float,
    threshold: float,
    *,
    direction: float = 1.0,
) -> float:
    """
    Margen firmado respecto al umbral.

        margin > 0:
            distancia disponible en la dirección definida.

    direction debe ser +1 o -1.
    """

    if direction not in {-1.0, 1.0}:
        raise ModelInputError(
            "direction debe ser +1 o -1."
        )

    return float(
        direction * (threshold - state)
    )


def threshold_breach(
    state: float,
    threshold: float,
    *,
    direction: float = 1.0,
) -> bool:
    margin = threshold_margin(
        state,
        threshold,
        direction=direction,
    )

    return bool(
        margin <= 0
    )


def first_threshold_crossing(
    values: Sequence[float],
    threshold: float,
    *,
    direction: float = 1.0,
) -> int | None:
    arr = _vector(
        values,
        name="values",
    )

    margins = direction * (
        threshold - arr
    )

    indices = np.flatnonzero(
        margins <= 0
    )

    if indices.size == 0:
        return None

    return int(
        indices[0]
    )


# ============================================================================
# PROPAGACIÓN Y CASCADAS
# ============================================================================


@dataclass(frozen=True, slots=True)
class PropagationState:
    """
    Estado de propagación entre unidades.

    propagation_ratio > 1 puede representar una condición de expansión
    del modelo, pero no equivale automáticamente a una cascada real.
    """

    propagation_ratio: float
    branching_factor: float
    spectral_radius: float

    potentially_amplifying: bool


def propagation_state(
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
    *,
    activated_previous: float,
    activated_current: float,
) -> PropagationState:
    if activated_previous < 0:
        raise ModelInputError(
            "activated_previous no puede ser negativo."
        )

    if activated_current < 0:
        raise ModelInputError(
            "activated_current no puede ser negativo."
        )

    ratio = _safe_ratio(
        activated_current,
        activated_previous,
    )

    W = _matrix(
        interaction_matrix,
        name="interaction_matrix",
    )

    branching = float(
        np.mean(
            np.sum(W, axis=1)
        )
    )

    spectral = coupling_spectral_radius(
        W
    )

    return PropagationState(
        propagation_ratio=ratio,
        branching_factor=branching,
        spectral_radius=spectral,
        potentially_amplifying=bool(
            ratio > 1.0
            or spectral > 1.0
        ),
    )


def propagate_state(
    state: Sequence[float],
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
    *,
    gain: float = 1.0,
) -> np.ndarray:
    """
    Propagación lineal de primer orden:

        X(t+1) = X(t) + gain · W X(t)

    Es una primitiva de dinámica de redes.

    No representa causalidad validada por sí misma.
    """

    x = _vector(
        state,
        name="state",
    )

    W = _matrix(
        interaction_matrix,
        name="interaction_matrix",
    )

    if W.shape != (x.size, x.size):
        raise ModelInputError(
            "interaction_matrix debe ser n × n."
        )

    if gain < 0:
        raise ModelInputError(
            "gain no puede ser negativo."
        )

    return x + gain * (W @ x)


def cascade_generation_count(
    generations: Sequence[Sequence[float]] | np.ndarray,
    *,
    activation_threshold: float = 0.0,
) -> int:
    """
    Número de generaciones activas observadas.

    Esto solo representa profundidad de cascada si las filas de `generations`
    corresponden realmente a generaciones temporales/causales.
    """

    matrix = _matrix(
        generations,
        name="generations",
    )

    if activation_threshold < 0:
        raise ModelInputError(
            "activation_threshold no puede ser negativo."
        )

    active = np.any(
        matrix > activation_threshold,
        axis=1,
    )

    return int(
        np.sum(active)
    )


# ============================================================================
# RECUPERACIÓN Y RESILIENCIA
# ============================================================================


def recovery_fraction(
    baseline: float,
    current: float,
    *,
    lower_is_better: bool = False,
) -> float:
    """
    Fracción de recuperación entre un estado alterado y baseline.

    Para variables donde mayor = mejor:

        (current - altered) / (baseline - altered)

    Para variables donde menor = mejor, se invierte la dirección.

    La función se utiliza para describir recuperación observada,
    no para inferir causalidad.
    """

    if baseline == current:
        return 1.0

    if lower_is_better:
        return _bounded(
            current / max(
                baseline,
                _EPS,
            )
        )

    return _bounded(
        current / max(
            baseline,
            _EPS,
        )
    )


def recovery_time(
    timestamps: Sequence[float],
    values: Sequence[float],
    *,
    target_fraction: float = 0.90,
) -> float | None:
    """
    Tiempo necesario para alcanzar una fracción del valor final.

    No presupone una forma paramétrica de recuperación.
    """

    time = _vector(
        timestamps,
        name="timestamps",
    )

    value = _vector(
        values,
        name="values",
    )

    _same_shape(
        time,
        value,
        names="timestamps y values",
    )

    if time.size < 2:
        raise ModelInputError(
            "Se necesitan al menos dos observaciones."
        )

    if not 0.0 < target_fraction <= 1.0:
        raise ModelInputError(
            "target_fraction debe estar en (0, 1]."
        )

    initial = float(
        value[0]
    )

    final = float(
        value[-1]
    )

    target = initial + target_fraction * (
        final - initial
    )

    direction = np.sign(
        final - initial
    )

    if direction == 0:
        return 0.0

    for index in range(1, value.size):

        reached = (
            value[index] >= target
            if direction > 0
            else value[index] <= target
        )

        if reached:
            return float(
                time[index] - time[0]
            )

    return None


def resilience_ratio(
    recovery_time_value: float | None,
    reference_time: float,
) -> float | None:
    """
    Menor tiempo de recuperación = mayor capacidad de recuperación.

        resilience = reference_time / recovery_time
    """

    if reference_time <= 0:
        raise ModelInputError(
            "reference_time debe ser > 0."
        )

    if recovery_time_value is None:
        return None

    if recovery_time_value <= 0:
        return float("inf")

    return float(
        reference_time
        / recovery_time_value
    )


# ============================================================================
# HOSTILIDAD, POLARIZACIÓN Y TENSIÓN SOCIAL
# ============================================================================


@dataclass(frozen=True, slots=True)
class SocialTensionState:
    """
    Señales agregadas de tensión social.

    IMPORTANTE:

    Estos valores representan observaciones agregadas del sistema,
    no atributos inherentes de personas, nacionalidades o colectivos.

    El módulo no produce un "índice de peligrosidad".
    """

    tension_level: float

    tension_velocity: float
    polarization: float
    disagreement: float

    uncertainty: float

    provenance_count: int

    def validate(self) -> None:
        if self.tension_level < 0:
            raise ModelInputError(
                "tension_level no puede ser negativa."
            )

        if not 0.0 <= self.polarization <= 1.0:
            raise ModelInputError(
                "polarization debe estar en [0, 1]."
            )

        if not 0.0 <= self.disagreement <= 1.0:
            raise ModelInputError(
                "disagreement debe estar en [0, 1]."
            )

        if not 0.0 <= self.uncertainty <= 1.0:
            raise ModelInputError(
                "uncertainty debe estar en [0, 1]."
            )

        if self.provenance_count < 0:
            raise ModelInputError(
                "provenance_count no puede ser negativo."
            )


def social_tension_velocity(
    tension: Sequence[float],
    timestamps: Sequence[float],
) -> np.ndarray:
    trajectory = build_dynamic_trajectory(
        timestamps,
        tension,
    )

    return np.asarray(
        trajectory.velocity
    )


def polarization_index(
    cross_group_interaction: float,
    within_group_interaction: float,
) -> float:
    """
    Diferencia normalizada entre interacción intragrupo y entre grupos.

    Debe utilizarse únicamente cuando la semántica de las categorías
    y la construcción de las interacciones estén explícitamente definidas.

    No es un "índice de odio".
    """

    denominator = (
        abs(within_group_interaction)
        + abs(cross_group_interaction)
    )

    if denominator <= _EPS:
        return 0.0

    return _bounded(
        abs(
            within_group_interaction
            - cross_group_interaction
        )
        / denominator
    )


def hostility_signal_composite(
    *,
    observed_hostility_rate: float,
    hostility_velocity: float,
    polarization: float,
    disagreement: float,
    uncertainty: float,
) -> float:
    """
    Señal estructural agregada de tensión.

    No es una probabilidad.

    No es un diagnóstico.

    No es un atributo individual.

    No es un indicador de peligrosidad de un grupo.

    La incertidumbre reduce la fuerza interpretativa de la señal.
    """

    if observed_hostility_rate < 0:
        raise ModelInputError(
            "observed_hostility_rate no puede ser negativa."
        )

    if not 0.0 <= polarization <= 1.0:
        raise ModelInputError(
            "polarization debe estar en [0, 1]."
        )

    if not 0.0 <= disagreement <= 1.0:
        raise ModelInputError(
            "disagreement debe estar en [0, 1]."
        )

    if not 0.0 <= uncertainty <= 1.0:
        raise ModelInputError(
            "uncertainty debe estar en [0, 1]."
        )

    positive_velocity = max(
        0.0,
        hostility_velocity,
    )

    raw = (
        observed_hostility_rate
        + positive_velocity
        + polarization
        + disagreement
    ) / 4.0

    return float(
        raw * (1.0 - uncertainty)
    )


# ============================================================================
# INFORMACIÓN COMO VARIABLE DEL SISTEMA
# ============================================================================


@dataclass(frozen=True, slots=True)
class InformationState:
    """
    Información → percepción → conducta → sistema.

    El modelo no asume que la información sea únicamente una variable
    descriptiva: puede modificar la dinámica del sistema.
    """

    information_volume: float
    uncertainty: float

    perception_change: float
    behavioural_response: float

    source_diversity: float

    feedback_gain: float

    def validate(self) -> None:
        if self.information_volume < 0:
            raise ModelInputError(
                "information_volume no puede ser negativo."
            )

        for name, value in (
            ("uncertainty", self.uncertainty),
            ("source_diversity", self.source_diversity),
        ):
            if not 0.0 <= value <= 1.0:
                raise ModelInputError(
                    f"{name} debe estar en [0, 1]."
                )


def information_feedback(
    information_change: float,
    behavioural_response: float,
) -> float:
    """
    Ganancia de realimentación informacional:

        G = Δbehaviour / Δinformation
    """

    if abs(information_change) <= _EPS:
        raise ModelInputError(
            "information_change demasiado pequeño."
        )

    return float(
        behavioural_response
        / information_change
    )


def reflexivity_update(
    system_state: float,
    information_signal: float,
    behavioural_gain: float,
) -> float:
    """
    Estado siguiente bajo realimentación informacional:

        X(t+1) = X(t) + G · I(t)
    """

    return float(
        system_state
        + behavioural_gain * information_signal
    )


# ============================================================================
# HIPÓTESIS COMPETIDORAS
# ============================================================================


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """
    Hipótesis falsable.

    Una hipótesis no se convierte en hecho por estar registrada.
    """

    hypothesis_id: str

    statement: str

    supporting_evidence_ids: tuple[str, ...]
    contradicting_evidence_ids: tuple[str, ...]

    predictions: tuple[str, ...]

    falsification_conditions: tuple[str, ...]

    status: EpistemicStatus = EpistemicStatus.HYPOTHESIS

    def validate(self) -> None:
        if not self.hypothesis_id.strip():
            raise ModelEpistemicError(
                "La hipótesis requiere un ID."
            )

        if not self.statement.strip():
            raise ModelEpistemicError(
                "La hipótesis requiere una formulación."
            )

        if not self.falsification_conditions:
            raise ModelEpistemicError(
                f"La hipótesis {self.hypothesis_id} "
                "no tiene condiciones explícitas de falsación."
            )

        if self.status != EpistemicStatus.HYPOTHESIS:
            raise ModelEpistemicError(
                "Hypothesis debe conservar estado epistemológico "
                "'hypothesis'."
            )


def compare_hypotheses(
    hypotheses: Sequence[Hypothesis],
) -> tuple[Hypothesis, ...]:
    """
    Valida y devuelve las hipótesis competidoras sin ordenarlas
    artificialmente por una puntuación de confianza.
    """

    if not hypotheses:
        raise ModelEpistemicError(
            "Debe existir al menos una hipótesis."
        )

    for hypothesis in hypotheses:
        hypothesis.validate()

    return tuple(
        hypotheses
    )


# ============================================================================
# ESCENARIOS
# ============================================================================


@dataclass(frozen=True, slots=True)
class Scenario:
    """
    Escenario condicional.

    Un escenario no es una predicción.
    """

    scenario_id: str

    name: str

    assumptions: tuple[str, ...]

    drivers: tuple[str, ...]
    constraints: tuple[str, ...]

    expected_mechanisms: tuple[str, ...]

    falsification_conditions: tuple[str, ...]

    epistemic_status: EpistemicStatus = EpistemicStatus.SCENARIO

    def validate(self) -> None:
        if not self.scenario_id.strip():
            raise ModelEpistemicError(
                "El escenario requiere un ID."
            )

        if not self.assumptions:
            raise ModelEpistemicError(
                f"El escenario {self.scenario_id} no tiene supuestos."
            )

        if not self.falsification_conditions:
            raise ModelEpistemicError(
                f"El escenario {self.scenario_id} no tiene "
                "condiciones de falsación."
            )

        if self.epistemic_status != EpistemicStatus.SCENARIO:
            raise ModelEpistemicError(
                "Scenario debe conservar estado epistemológico "
                "'scenario'."
            )


# ============================================================================
# SUSCEPTIBILIDAD SISTÉMICA
# ============================================================================


@dataclass(frozen=True, slots=True)
class SystemSusceptibility:
    """
    Susceptibilidad estructural del sistema.

    No es probabilidad de daño.

    Integra:

        pressure
        reserve depletion
        coupling
        sensitivity
        threshold proximity
        propagation
        recovery limitation
    """

    pressure: float
    reserve_depletion: float
    coupling: float
    sensitivity: float
    threshold_proximity: float
    propagation: float
    recovery_constraint: float

    susceptibility: float

    epistemic_status: EpistemicStatus = (
        EpistemicStatus.CALCULATED
    )

    def validate(self) -> None:
        components = (
            self.pressure,
            self.reserve_depletion,
            self.coupling,
            self.sensitivity,
            self.threshold_proximity,
            self.propagation,
            self.recovery_constraint,
        )

        for value in components:
            if value < 0:
                raise ModelInputError(
                    "Los componentes de susceptibilidad "
                    "no pueden ser negativos."
                )

        if self.susceptibility < 0:
            raise ModelInputError(
                "susceptibility no puede ser negativa."
            )


def systemic_susceptibility(
    *,
    pressure: float,
    reserve_depletion: float,
    coupling: float,
    sensitivity: float,
    threshold_proximity: float,
    propagation: float,
    recovery_constraint: float,
) -> SystemSusceptibility:
    """
    Modelo estructural multiplicativo.

        S = P · R · C · G · T · Q · H

    donde cada componente representa una dimensión distinta.

    La multiplicación expresa una hipótesis estructural:

    una combinación de múltiples vulnerabilidades simultáneas puede
    amplificar la susceptibilidad.

    No debe interpretarse como probabilidad de muerte, violencia,
    delito o daño sin validación específica.
    """

    components = {
        "pressure": pressure,
        "reserve_depletion": reserve_depletion,
        "coupling": coupling,
        "sensitivity": sensitivity,
        "threshold_proximity": threshold_proximity,
        "propagation": propagation,
        "recovery_constraint": recovery_constraint,
    }

    for name, value in components.items():

        if value < 0:
            raise ModelInputError(
                f"{name} no puede ser negativo."
            )

        if not isfinite(float(value)):
            raise ModelInputError(
                f"{name} debe ser finito."
            )

    susceptibility = float(
        pressure
        * reserve_depletion
        * coupling
        * sensitivity
        * threshold_proximity
        * propagation
        * recovery_constraint
    )

    result = SystemSusceptibility(
        pressure=float(pressure),
        reserve_depletion=float(reserve_depletion),
        coupling=float(coupling),
        sensitivity=float(sensitivity),
        threshold_proximity=float(
            threshold_proximity
        ),
        propagation=float(propagation),
        recovery_constraint=float(
            recovery_constraint
        ),
        susceptibility=susceptibility,
    )

    result.validate()

    return result


# ============================================================================
# MODELO DINÁMICO CANÓNICO DE CeutIA
# ============================================================================


@dataclass(frozen=True, slots=True)
class CeutIADynamicState:
    """
    Estado integrado de CeutIA.

    Esta estructura reúne las dimensiones fundamentales de la teoría de
    Medicina Dinámica aplicada a un sistema complejo territorial.

        X(t+1) = F(
            X(t),
            U(t),
            E(t),
            Θ(t)
        ) + ε(t)

    donde:

        X = estado del sistema
        U = intervenciones/respuesta
        E = perturbaciones/exposición
        Θ = parámetros/contexto
        ε = incertidumbre/residuo
    """

    state: Mapping[str, float]

    velocity: Mapping[str, float]
    acceleration: Mapping[str, float]

    load: Mapping[str, float]
    reserve: Mapping[str, float]

    capacity: Mapping[str, float]
    coupling: float

    sensitivity: float
    propagation: float

    threshold_proximity: float

    recovery: Mapping[str, float]

    information_feedback: float

    social_tension: float

    uncertainty: float

    epistemic_status: EpistemicStatus = (
        EpistemicStatus.CALCULATED
    )


@dataclass(frozen=True, slots=True)
class SystemRiskSignal:
    """
    Señal de riesgo sistémico.

    Es una salida analítica PRIVATE/INTERNAL potencial.

    No constituye una decisión.

    No constituye una probabilidad de peligrosidad individual o grupal.
    """

    signal_id: str

    domain: ModelDomain

    target: RiskTarget

    output_type: ModelOutputType

    magnitude: float

    trajectory: float

    severity_proxy: float

    uncertainty: float

    epistemic_status: EpistemicStatus

    spatial_units: tuple[str, ...]

    mechanisms: tuple[str, ...]

    evidence_ids: tuple[str, ...]

    limitations: tuple[str, ...]

    human_interpretation_required: bool = True

    def validate(self) -> None:
        if not self.signal_id.strip():
            raise ModelInputError(
                "signal_id no puede estar vacío."
            )

        if self.target in {
            RiskTarget.INDIVIDUAL,
            RiskTarget.GROUP,
        }:
            raise ModelSafetyError(
                "CeutIA no puede convertir esta arquitectura "
                "en un modelo operacional de peligrosidad "
                "individual o grupal."
            )

        if not isfinite(
            float(self.magnitude)
        ):
            raise ModelInputError(
                "magnitude debe ser finita."
            )

        if not 0.0 <= self.uncertainty <= 1.0:
            raise ModelInputError(
                "uncertainty debe estar en [0, 1]."
            )

        if not self.human_interpretation_required:
            raise ModelSafetyError(
                "Toda señal de riesgo requiere interpretación humana."
            )


# ============================================================================
# CONSTRUCCIÓN DEL ESTADO CANÓNICO
# ============================================================================


def build_system_state(
    *,
    state: Mapping[str, float],
    velocity: Mapping[str, float],
    acceleration: Mapping[str, float],
    load: Mapping[str, float],
    reserve: Mapping[str, float],
    capacity: Mapping[str, float],
    coupling: float,
    sensitivity: float,
    propagation: float,
    threshold_proximity: float,
    recovery: Mapping[str, float],
    information_feedback: float,
    social_tension: float,
    uncertainty: float,
) -> CeutIADynamicState:
    """
    Construye el estado dinámico canónico.

    No intenta reducir todas las dimensiones a un único número.
    """

    for mapping_name, mapping in (
        ("state", state),
        ("velocity", velocity),
        ("acceleration", acceleration),
        ("load", load),
        ("reserve", reserve),
        ("capacity", capacity),
        ("recovery", recovery),
    ):
        for key, value in mapping.items():

            if not isfinite(float(value)):
                raise ModelInputError(
                    f"{mapping_name}[{key}] no es finito."
                )

    scalar_values = {
        "coupling": coupling,
        "sensitivity": sensitivity,
        "propagation": propagation,
        "threshold_proximity": threshold_proximity,
        "information_feedback": information_feedback,
        "social_tension": social_tension,
    }

    for name, value in scalar_values.items():

        if not isfinite(float(value)):
            raise ModelInputError(
                f"{name} debe ser finito."
            )

    if not 0.0 <= uncertainty <= 1.0:
        raise ModelInputError(
            "uncertainty debe estar en [0, 1]."
        )

    return CeutIADynamicState(
        state=dict(state),
        velocity=dict(velocity),
        acceleration=dict(acceleration),
        load=dict(load),
        reserve=dict(reserve),
        capacity=dict(capacity),
        coupling=float(coupling),
        sensitivity=float(sensitivity),
        propagation=float(propagation),
        threshold_proximity=float(
            threshold_proximity
        ),
        recovery=dict(recovery),
        information_feedback=float(
            information_feedback
        ),
        social_tension=float(
            social_tension
        ),
        uncertainty=float(
            uncertainty
        ),
    )


# ============================================================================
# TRANSICIÓN DINÁMICA
# ============================================================================


def dynamic_transition_score(
    *,
    velocity: float,
    acceleration: float,
    reserve_depletion: float,
    threshold_proximity: float,
    coupling: float,
    propagation: float,
    uncertainty: float,
) -> float:
    """
    Señal compuesta de susceptibilidad a transición.

    El objetivo es detectar configuración dinámica:

        cambio rápido
        +
        aceleración
        +
        reserva reducida
        +
        proximidad al umbral
        +
        acoplamiento
        +
        propagación

    No es probabilidad de transición.

    La incertidumbre atenúa la interpretabilidad.
    """

    values = (
        velocity,
        acceleration,
        reserve_depletion,
        threshold_proximity,
        coupling,
        propagation,
    )

    for value in values:

        if value < 0:
            raise ModelInputError(
                "Los componentes no pueden ser negativos."
            )

    if not 0.0 <= uncertainty <= 1.0:
        raise ModelInputError(
            "uncertainty debe estar en [0, 1]."
        )

    raw = (
        velocity
        * (1.0 + acceleration)
        * (1.0 + reserve_depletion)
        * (1.0 + threshold_proximity)
        * (1.0 + coupling)
        * (1.0 + propagation)
    )

    return float(
        raw * (1.0 - uncertainty)
    )


# ============================================================================
# DINÁMICA TERRITORIAL INTEGRADA
# ============================================================================


def territorial_systemic_signal(
    *,
    demand: Sequence[float],
    capacity: Sequence[float],
    reserve: Sequence[float],
    exposure: Sequence[float],
    interaction_matrix: Sequence[Sequence[float]] | np.ndarray,
    previous_load: Sequence[float] | None = None,
    current_load: Sequence[float] | None = None,
) -> np.ndarray:
    """
    Produce una señal territorial multidimensional por unidad.

    Integra:

        utilización
        exposición
        agotamiento de reserva
        presión espacial
        variación de carga

    La salida es una señal descriptiva de presión/fragilidad,
    no una predicción de daño.
    """

    demand_arr = _vector(
        demand,
        name="demand",
    )

    capacity_arr = _vector(
        capacity,
        name="capacity",
    )

    reserve_arr = _vector(
        reserve,
        name="reserve",
    )

    exposure_arr = _vector(
        exposure,
        name="exposure",
    )

    n = demand_arr.size

    if capacity_arr.size != n:
        raise ModelInputError(
            "capacity debe tener el mismo tamaño que demand."
        )

    if reserve_arr.size != n:
        raise ModelInputError(
            "reserve debe tener el mismo tamaño que demand."
        )

    if exposure_arr.size != n:
        raise ModelInputError(
            "exposure debe tener el mismo tamaño que demand."
        )

    utilization = demand_arr / np.maximum(
        capacity_arr,
        _EPS,
    )

    reserve_depletion = 1.0 - (
        reserve_arr
        / np.maximum(
            np.max(reserve_arr),
            _EPS,
        )
    )

    spatial_pressure = territorial_spatial_lag(
        utilization,
        interaction_matrix,
    )

    if previous_load is None or current_load is None:

        load_change = np.zeros(
            n,
            dtype=float,
        )

    else:

        previous = _vector(
            previous_load,
            name="previous_load",
        )

        current = _vector(
            current_load,
            name="current_load",
        )

        _same_shape(
            previous,
            demand_arr,
            names="previous_load y demand",
        )

        _same_shape(
            current,
            demand_arr,
            names="current_load y demand",
        )

        load_change = np.maximum(
            current - previous,
            0.0,
        )

    result = (
        np.maximum(
            utilization,
            0.0,
        )
        * (
            1.0
            + np.maximum(
                exposure_arr,
                0.0,
            )
        )
        * (
            1.0
            + np.maximum(
                reserve_depletion,
                0.0,
            )
        )
        * (
            1.0
            + np.maximum(
                spatial_pressure,
                0.0,
            )
        )
        * (
            1.0
            + load_change
        )
    )

    return result


# ============================================================================
# PEQUEÑO ESTÍMULO + ALTA SENSIBILIDAD + ALTA PROPAGACIÓN
# ============================================================================


def small_stimulus_cascade_susceptibility(
    *,
    stimulus: float,
    local_sensitivity_value: float,
    reserve_depletion: float,
    coupling: float,
    propagation: float,
    threshold_proximity: float,
    recovery_constraint: float,
    social_tension: float,
    uncertainty: float,
) -> float:
    """
    Estructura matemática para la hipótesis:

        pequeño estímulo
            +
        baja reserva
            +
        alta sensibilidad
            +
        alto acoplamiento
            +
        alta propagación
            +
        proximidad al umbral
            +
        baja capacidad de recuperación
            +
        tensión social
            →
        mayor susceptibilidad sistémica

    IMPORTANTE:

    Esta función NO afirma que el resultado ocurra.

    No predice número de muertos.

    No predice delitos.

    No predice peligrosidad individual.

    Es una magnitud de SUSCEPTIBILIDAD estructural que deberá ser
    validada retrospectivamente si se pretende utilizar operacionalmente.
    """

    values = {
        "stimulus": stimulus,
        "local_sensitivity": local_sensitivity_value,
        "reserve_depletion": reserve_depletion,
        "coupling": coupling,
        "propagation": propagation,
        "threshold_proximity": threshold_proximity,
        "recovery_constraint": recovery_constraint,
        "social_tension": social_tension,
    }

    for name, value in values.items():

        if value < 0:
            raise ModelInputError(
                f"{name} no puede ser negativo."
            )

    if not 0.0 <= uncertainty <= 1.0:
        raise ModelInputError(
            "uncertainty debe estar en [0, 1]."
        )

    stimulus_factor = (
        1.0
        if stimulus <= _EPS
        else min(
            1.0,
            stimulus,
        )
    )

    structural_gain = (
        local_sensitivity_value
        * (1.0 + reserve_depletion)
        * (1.0 + coupling)
        * (1.0 + propagation)
        * (1.0 + threshold_proximity)
        * (1.0 + recovery_constraint)
        * (1.0 + social_tension)
    )

    return float(
        stimulus_factor
        * structural_gain
        * (1.0 - uncertainty)
    )


# ============================================================================
# MODELO DE CASCADA SISTÉMICA
# ============================================================================


@dataclass(frozen=True, slots=True)
class CascadeAssessment:
    """
    Evaluación de condiciones de cascada.

    No afirma que una cascada vaya a producirse.
    """

    amplification_condition: bool
    threshold_condition: bool
    reserve_condition: bool
    propagation_condition: bool
    recovery_condition: bool

    active_conditions: int
    susceptibility: float

    def validate(self) -> None:
        if not 0 <= self.active_conditions <= 5:
            raise ModelInputError(
                "active_conditions debe estar entre 0 y 5."
            )


def assess_cascade_conditions(
    *,
    amplification: float,
    threshold_breach: bool,
    reserve_depletion: float,
    propagation_ratio_value: float,
    recovery_fraction_value: float,
) -> CascadeAssessment:
    """
    Identifica condiciones necesarias/compatibles con una posible cascada.

    No las trata como suficientes.
    """

    if amplification < 0:
        raise ModelInputError(
            "amplification no puede ser negativa."
        )

    if not 0.0 <= reserve_depletion <= 1.0:
        raise ModelInputError(
            "reserve_depletion debe estar en [0, 1]."
        )

    if propagation_ratio_value < 0:
        raise ModelInputError(
            "propagation_ratio no puede ser negativo."
        )

    if not 0.0 <= recovery_fraction_value <= 1.0:
        raise ModelInputError(
            "recovery_fraction debe estar en [0, 1]."
        )

    amplification_condition = (
        amplification > 1.0
    )

    threshold_condition = bool(
        threshold_breach
    )

    reserve_condition = (
        reserve_depletion >= 0.50
    )

    propagation_condition = (
        propagation_ratio_value > 1.0
    )

    recovery_condition = (
        recovery_fraction_value < 0.50
    )

    conditions = (
        amplification_condition,
        threshold_condition,
        reserve_condition,
        propagation_condition,
        recovery_condition,
    )

    active = sum(
        bool(condition)
        for condition in conditions
    )

    susceptibility = (
        active / 5.0
    )

    result = CascadeAssessment(
        amplification_condition=amplification_condition,
        threshold_condition=threshold_condition,
        reserve_condition=reserve_condition,
        propagation_condition=propagation_condition,
        recovery_condition=recovery_condition,
        active_conditions=active,
        susceptibility=float(susceptibility),
    )

    result.validate()

    return result


# ============================================================================
# CONSTRUCCIÓN DE SEÑALES
# ============================================================================


def build_system_risk_signal(
    *,
    signal_id: str,
    domain: ModelDomain,
    magnitude: float,
    trajectory: float,
    severity_proxy: float,
    uncertainty: float,
    spatial_units: Sequence[str],
    mechanisms: Sequence[str],
    evidence_ids: Sequence[str],
    output_type: ModelOutputType = ModelOutputType.SUSCEPTIBILITY,
    target: RiskTarget = RiskTarget.SYSTEM,
    epistemic_status: EpistemicStatus = EpistemicStatus.CALCULATED,
) -> SystemRiskSignal:
    """
    Construye una señal sistémica segura.
    """

    signal = SystemRiskSignal(
        signal_id=signal_id,
        domain=domain,
        target=target,
        output_type=output_type,
        magnitude=float(magnitude),
        trajectory=float(trajectory),
        severity_proxy=float(severity_proxy),
        uncertainty=float(uncertainty),
        epistemic_status=epistemic_status,
        spatial_units=tuple(
            spatial_units
        ),
        mechanisms=tuple(
            mechanisms
        ),
        evidence_ids=tuple(
            evidence_ids
        ),
        limitations=(
            "La señal describe una condición sistémica.",
            "No constituye una predicción individual.",
            "No constituye una atribución causal automática.",
            "Requiere interpretación humana.",
        ),
    )

    signal.validate()

    return signal


# ============================================================================
# PREDICCIÓN: BLOQUEO EPISTÉMICO
# ============================================================================


@dataclass(frozen=True, slots=True)
class PredictionQualification:
    """
    Requisitos mínimos para una predicción cuantitativa.

    La ausencia de cualquiera de ellos impide tratar la salida como
    predicción operacional.
    """

    outcome_defined: bool
    horizon_defined: bool
    appropriate_data: bool
    temporally_validated: bool
    externally_validated: bool
    calibrated: bool
    out_of_sample_evaluated: bool

    @property
    def operationally_qualified(self) -> bool:
        return all(
            (
                self.outcome_defined,
                self.horizon_defined,
                self.appropriate_data,
                self.temporally_validated,
                self.externally_validated,
                self.calibrated,
                self.out_of_sample_evaluated,
            )
        )


def require_prediction_qualification(
    qualification: PredictionQualification,
) -> None:
    """
    Bloquea una predicción operacional si no se cumplen todos los requisitos.
    """

    if not qualification.operationally_qualified:

        raise ModelValidationError(
            "Predicción cuantitativa no cualificada para uso operacional."
        )


# ============================================================================
# INTEGRACIÓN DE HIPÓTESIS + MÉTRICAS + DINÁMICA
# ============================================================================


@dataclass(frozen=True, slots=True)
class IntegratedModelAssessment:
    """
    Resultado integrado del modelo dinámico.

    Conserva las dimensiones por separado para evitar que un único score
    oculte la estructura del sistema.
    """

    state: CeutIADynamicState

    systemic_susceptibility: float

    transition_susceptibility: float

    cascade: CascadeAssessment

    hypotheses: tuple[Hypothesis, ...]

    scenarios: tuple[Scenario, ...]

    signals: tuple[SystemRiskSignal, ...]

    epistemic_status: EpistemicStatus

    uncertainty: float

    human_interpretation_required: bool = True

    def validate(self) -> None:
        if self.systemic_susceptibility < 0:
            raise ModelInputError(
                "systemic_susceptibility no puede ser negativa."
            )

        if self.transition_susceptibility < 0:
            raise ModelInputError(
                "transition_susceptibility no puede ser negativa."
            )

        if not 0.0 <= self.uncertainty <= 1.0:
            raise ModelInputError(
                "uncertainty debe estar en [0, 1]."
            )

        if not self.human_interpretation_required:
            raise ModelSafetyError(
                "La interpretación humana es obligatoria."
            )

        for hypothesis in self.hypotheses:
            hypothesis.validate()

        for scenario in self.scenarios:
            scenario.validate()

        for signal in self.signals:
            signal.validate()


def integrate_dynamic_assessment(
    *,
    state: CeutIADynamicState,
    systemic_susceptibility_value: float,
    transition_susceptibility: float,
    cascade: CascadeAssessment,
    hypotheses: Sequence[Hypothesis] = (),
    scenarios: Sequence[Scenario] = (),
    signals: Sequence[SystemRiskSignal] = (),
    uncertainty: float,
) -> IntegratedModelAssessment:
    """
    Integra las dimensiones del modelo sin reducirlas prematuramente
    a una única puntuación.

    La incertidumbre se conserva explícitamente.
    """

    if systemic_susceptibility_value < 0:
        raise ModelInputError(
            "systemic_susceptibility_value no puede ser negativa."
        )

    if transition_susceptibility < 0:
        raise ModelInputError(
            "transition_susceptibility no puede ser negativa."
        )

    if not 0.0 <= uncertainty <= 1.0:
        raise ModelInputError(
            "uncertainty debe estar en [0, 1]."
        )

    integrated = IntegratedModelAssessment(
        state=state,
        systemic_susceptibility=float(
            systemic_susceptibility_value
        ),
        transition_susceptibility=float(
            transition_susceptibility
        ),
        cascade=cascade,
        hypotheses=tuple(
            hypotheses
        ),
        scenarios=tuple(
            scenarios
        ),
        signals=tuple(
            signals
        ),
        epistemic_status=EpistemicStatus.CALCULATED,
        uncertainty=float(
            uncertainty
        ),
        human_interpretation_required=True,
    )

    integrated.validate()

    return integrated


# ============================================================================
# INVARIANTES FUNDAMENTALES DE CeutIA
# ============================================================================


MODEL_INVARIANTS: Final[tuple[str, ...]] = (

    "El estado instantáneo no sustituye a la trayectoria.",

    "La trayectoria debe poder representarse mediante nivel, velocidad "
    "y aceleración cuando la resolución temporal lo permita.",

    "Carga acumulada y reserva adaptativa son variables diferentes.",

    "Capacidad global no equivale necesariamente a capacidad efectiva "
    "ni a capacidad accesible.",

    "La utilización de capacidad debe conservar su dimensión temporal.",

    "Un aumento de demanda no implica por sí mismo una crisis.",

    "La crisis depende de la interacción entre demanda, capacidad, "
    "reserva, tiempo, concentración y recuperación.",

    "La concentración territorial debe conservar la unidad espacial "
    "utilizada para calcularla.",

    "La pequeña superficie física de Ceuta no implica automáticamente "
    "alto acoplamiento; el acoplamiento debe modelarse mediante "
    "movilidad, infraestructura, distancia, servicios y redes.",

    "La proximidad espacial no demuestra causalidad.",

    "El acoplamiento puede amplificar perturbaciones, pero su presencia "
    "no demuestra que vaya a producirse una cascada.",

    "La sensibilidad a pequeños estímulos debe distinguirse de la "
    "magnitud del estímulo.",

    "Una respuesta desproporcionada es una señal de no linealidad o "
    "sensibilidad, no automáticamente una predicción de daño.",

    "La proximidad a un umbral no demuestra transición crítica.",

    "Un early-warning signal no demuestra que una transición vaya a ocurrir.",

    "Una cascada requiere diferenciar estímulo, propagación, amplificación "
    "y recuperación.",

    "Hostilidad, tensión y polarización son variables agregadas del sistema "
    "cuando están operacionalizadas mediante observaciones apropiadas.",

    "Hostilidad no es una propiedad inherente de una nacionalidad, origen "
    "o colectivo.",

    "Migración no puede utilizarse como proxy automático de criminalidad.",

    "Las señales de violencia describen eventos observables y dinámica "
    "del sistema, no peligrosidad inherente.",

    "Información, percepción y comportamiento forman potencialmente un "
    "bucle de realimentación.",

    "La vigilancia y la publicación de información pueden modificar el "
    "sistema observado; esto debe considerarse como contaminación por "
    "intervención o reflexividad.",

    "Una hipótesis debe tener condiciones explícitas de falsación.",

    "Las hipótesis competidoras deben conservarse cuando la evidencia "
    "no permite seleccionar una explicación.",

    "Un escenario no equivale a una predicción.",

    "Una predicción cuantitativa requiere outcome y horizonte definidos.",

    "La calibración no equivale a causalidad.",

    "La validación externa no sustituye automáticamente la validación "
    "temporal en Ceuta.",

    "La robustez estadística no equivale a robustez causal.",

    "La robustez computacional no equivale a verdad.",

    "La supervivencia de una prueba de refutación no equivale a verdad.",

    "La incertidumbre debe conservarse hasta la salida.",

    "No se deben fabricar probabilidades cuando el modelo no está "
    "validado para producirlas.",

    "Una señal de susceptibilidad no es una probabilidad de daño.",

    "Una señal sistémica no debe convertirse automáticamente en una "
    "afirmación individual.",

    "Las salidas de riesgo requieren interpretación humana.",

    "PRIVATE puede recibir inteligencia cualificada; PUBLIC no debe "
    "recibir automáticamente inteligencia PRIVATE.",

    "Este módulo no autoriza actuaciones de seguridad.",

    "La decisión operacional queda fuera del modelo matemático.",

    "Toda eventual escalada debe seguir la frontera de información "
    "y el proceso de supervisión humana de CeutIA.",
)


# ============================================================================
# INTEGRIDAD DEL MODELO
# ============================================================================


def validate_model_invariants() -> None:
    """
    Validación estructural de invariantes.

    Mantener esta función explícita permite incorporar posteriormente
    pruebas automáticas de arquitectura.
    """

    if not MODEL_INVARIANTS:
        raise ModelValidationError(
            "CeutIA requiere invariantes de modelo."
        )

    required_phrases = (
        "estado instantáneo",
        "trayectoria",
        "reserva",
        "acoplamiento",
        "hipótesis",
        "incertidumbre",
        "interpretación humana",
    )

    corpus = " ".join(
        MODEL_INVARIANTS
    ).lower()

    for phrase in required_phrases:

        if phrase not in corpus:
            raise ModelValidationError(
                f"Falta invariante estructural: {phrase}"
            )


validate_model_invariants()


# ============================================================================
# EXPORTS
# ============================================================================


__all__ = [
    "ModelDomain",
    "EpistemicStatus",
    "ModelStatus",
    "RiskTarget",
    "ModelOutputType",
    "ModelError",
    "ModelInputError",
    "ModelValidationError",
    "ModelSafetyError",
    "ModelEpistemicError",
    "DynamicState",
    "DynamicTrajectory",
    "ReserveState",
    "CapacityState",
    "TerritorialState",
    "PropagationState",
    "SocialTensionState",
    "InformationState",
    "Hypothesis",
    "Scenario",
    "SystemSusceptibility",
    "CeutIADynamicState",
    "SystemRiskSignal",
    "CascadeAssessment",
    "PredictionQualification",
    "IntegratedModelAssessment",
    "build_dynamic_trajectory",
    "adaptive_reserve_trajectory",
    "reserve_depletion_fraction",
    "reserve_headroom",
    "capacity_state",
    "capacity_trajectory",
    "first_bottleneck",
    "bottleneck_severity",
    "territorial_utilization",
    "territorial_spatial_lag",
    "normalized_interaction_matrix",
    "coupling_spectral_radius",
    "territorial_coupling_strength",
    "local_sensitivity",
    "local_elasticity",
    "amplification_factor",
    "regularized_transition_susceptibility",
    "threshold_distance",
    "threshold_margin",
    "threshold_breach",
    "first_threshold_crossing",
    "propagation_state",
    "propagate_state",
    "cascade_generation_count",
    "recovery_fraction",
    "recovery_time",
    "resilience_ratio",
    "social_tension_velocity",
    "polarization_index",
    "hostility_signal_composite",
    "information_feedback",
    "reflexivity_update",
    "compare_hypotheses",
    "systemic_susceptibility",
    "small_stimulus_cascade_susceptibility",
    "assess_cascade_conditions",
    "build_system_state",
    "dynamic_transition_score",
    "territorial_systemic_signal",
    "build_system_risk_signal",
    "require_prediction_qualification",
    "integrate_dynamic_assessment",
    "MODEL_INVARIANTS",
]
"""
CEUTIA PUBLIC — Core Domain Models.

Canonical domain contracts for the epistemic, evidentiary and analytical
layers of CEUTIA PUBLIC.

This module deliberately contains Pydantic domain models only.
Persistence models, API schemas and analytical implementations belong to
higher or adjacent layers.

Canonical epistemic chain:

    source
        -> artifact
        -> observation
        -> claim / event
        -> evidence
        -> signal
        -> inference
        -> hypothesis
        -> prediction
        -> scenario
        -> alert
        -> decision
        -> outcome

The models preserve:

- provenance;
- temporal semantics;
- spatial semantics;
- uncertainty;
- source independence;
- corroboration;
- contradiction;
- epistemic status;
- analytical lineage;
- model version;
- privacy classification;
- person/system separation;
- and explicit unknown states.

No model in this module determines whether a claim is true by itself.
These are contracts for representing knowledge and uncertainty.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ============================================================================
# COMMON TYPES
# ============================================================================


Probability = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
PositiveFloat = Annotated[float, Field(gt=0.0)]
NonNegativeInt = Annotated[int, Field(ge=0)]
PositiveInt = Annotated[int, Field(gt=0)]


class DomainModel(BaseModel):
    """Base configuration shared by all CEUTIA domain models."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


class IdentifiedModel(DomainModel):
    """Domain object with stable identity and creation timestamp."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value


class TemporalInterval(DomainModel):
    """
    Explicit temporal semantics.

    event_time:
        When the real-world event occurred.

    observation_time:
        When the system or observer observed/measured it.

    publication_time:
        When the information became publicly available.

    ingestion_time:
        When CEUTIA received the artifact.

    processing_time:
        When CEUTIA processed the artifact.
    """

    event_time: datetime | None = None
    observation_time: datetime | None = None
    publication_time: datetime | None = None
    ingestion_time: datetime | None = None
    processing_time: datetime | None = None

    effective_from: datetime | None = None
    effective_to: datetime | None = None

    @model_validator(mode="after")
    def validate_temporal_order(self) -> TemporalInterval:
        timestamps = {
            "event_time": self.event_time,
            "observation_time": self.observation_time,
            "publication_time": self.publication_time,
            "ingestion_time": self.ingestion_time,
            "processing_time": self.processing_time,
        }

        for name, timestamp in timestamps.items():
            if timestamp is not None and (
                timestamp.tzinfo is None or timestamp.utcoffset() is None
            ):
                raise ValueError(f"{name} must be timezone-aware")

        if self.effective_from and self.effective_to:
            if self.effective_to <= self.effective_from:
                raise ValueError("effective_to must be later than effective_from")

        return self


class SpatialReference(DomainModel):
    """
    Spatial semantics.

    A location may be represented at different resolutions.
    Exact coordinates are deliberately optional and should not be used
    unless necessary for the declared purpose.
    """

    place_id: str | None = None
    name: str | None = None
    administrative_level: str | None = None
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    spatial_resolution_m: NonNegativeFloat | None = None

    @model_validator(mode="after")
    def validate_coordinates(self) -> SpatialReference:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")

        return self


# ============================================================================
# CLASSIFICATION
# ============================================================================


class SensitivityClass(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"
    HIGHLY_RESTRICTED = "HIGHLY_RESTRICTED"


class DataSubjectClass(StrEnum):
    SYSTEM = "SYSTEM"
    AGGREGATE = "AGGREGATE"
    PERSON = "PERSON"
    UNKNOWN = "UNKNOWN"


class EpistemicStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    REPORTED = "REPORTED"
    CORROBORATED = "CORROBORATED"
    CONTRADICTED = "CONTRADICTED"
    INFERRED = "INFERRED"
    HYPOTHESIZED = "HYPOTHESIZED"
    PREDICTED = "PREDICTED"
    SCENARIO = "SCENARIO"
    DECIDED = "DECIDED"
    OUTCOME = "OUTCOME"


class EvidenceDirection(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    NEUTRAL = "NEUTRAL"
    CONTEXTUALIZES = "CONTEXTUALIZES"
    UNKNOWN = "UNKNOWN"


class SourceType(StrEnum):
    PRIMARY_INSTITUTIONAL = "PRIMARY_INSTITUTIONAL"
    SCIENTIFIC = "SCIENTIFIC"
    PROFESSIONAL_INTERNATIONAL = "PROFESSIONAL_INTERNATIONAL"
    REPUTABLE_MEDIA = "REPUTABLE_MEDIA"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    CITIZEN_TESTIMONY = "CITIZEN_TESTIMONY"
    SENSOR = "SENSOR"
    INTERNAL_SYSTEM = "INTERNAL_SYSTEM"
    UNKNOWN = "UNKNOWN"


class SourceAuthenticity(StrEnum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


class QualityLevel(StrEnum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class UncertaintyType(StrEnum):
    MEASUREMENT = "MEASUREMENT"
    SAMPLING = "SAMPLING"
    MODEL = "MODEL"
    TEMPORAL = "TEMPORAL"
    SPATIAL = "SPATIAL"
    REPORTING = "REPORTING"
    MISSINGNESS = "MISSINGNESS"
    SOURCE = "SOURCE"
    INTERPRETATION = "INTERPRETATION"
    STRUCTURAL = "STRUCTURAL"
    UNKNOWN = "UNKNOWN"


class MissingnessMechanism(StrEnum):
    NOT_MISSING = "NOT_MISSING"
    MCAR = "MCAR"
    MAR = "MAR"
    MNAR = "MNAR"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# SOURCE
# ============================================================================


class Source(IdentifiedModel):
    """
    Origin of information.

    A source is not equivalent to an individual claim.
    Source reliability and claim validity are separate concepts.
    """

    name: str = Field(min_length=1, max_length=500)
    source_type: SourceType
    uri: str | None = None
    publisher: str | None = None

    authenticity: SourceAuthenticity = SourceAuthenticity.UNKNOWN
    quality: QualityLevel = QualityLevel.UNKNOWN

    independence_group: str | None = None

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    @field_validator("first_seen_at", "last_seen_at")
    @classmethod
    def validate_source_timestamps(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("source timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_source_period(self) -> Source:
        if self.first_seen_at and self.last_seen_at:
            if self.last_seen_at < self.first_seen_at:
                raise ValueError("last_seen_at cannot precede first_seen_at")
        return self


# ============================================================================
# RAW ARTIFACT
# ============================================================================


class Artifact(IdentifiedModel):
    """
    Immutable representation of an ingested information artifact.

    Examples:
    - document;
    - dataset;
    - API response;
    - image;
    - video;
    - social-media publication;
    - citizen report.
    """

    source_id: UUID

    artifact_type: str = Field(min_length=1, max_length=100)
    content_hash: str = Field(min_length=1, max_length=256)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    language: str | None = Field(default=None, max_length=20)
    mime_type: str | None = Field(default=None, max_length=200)

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC
    subject_class: DataSubjectClass = DataSubjectClass.UNKNOWN

    integrity_verified: bool = False


# ============================================================================
# OBSERVATION / MEASUREMENT
# ============================================================================


class MeasurementUncertainty(DomainModel):
    """Explicit representation of measurement uncertainty."""

    uncertainty_type: UncertaintyType
    standard_error: NonNegativeFloat | None = None
    confidence_interval_lower: float | None = None
    confidence_interval_upper: float | None = None
    relative_uncertainty: NonNegativeFloat | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> MeasurementUncertainty:
        lower = self.confidence_interval_lower
        upper = self.confidence_interval_upper

        if (lower is None) != (upper is None):
            raise ValueError(
                "confidence_interval_lower and confidence_interval_upper "
                "must be supplied together"
            )

        if lower is not None and upper is not None and upper < lower:
            raise ValueError(
                "confidence_interval_upper must be greater than or equal "
                "to confidence_interval_lower"
            )

        return self


class Observation(IdentifiedModel):
    """
    Structured observation extracted from an artifact or direct sensor.

    An observation describes what was observed, not what it means.
    """

    artifact_id: UUID
    variable: str = Field(min_length=1, max_length=300)

    value: float | int | str | bool | None = None
    unit: str | None = Field(default=None, max_length=100)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    uncertainty: MeasurementUncertainty | None = None

    missingness: MissingnessMechanism = MissingnessMechanism.NOT_MISSING

    quality: QualityLevel = QualityLevel.UNKNOWN

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    @model_validator(mode="after")
    def validate_observation(self) -> Observation:
        if (
            self.missingness == MissingnessMechanism.NOT_MISSING
            and self.value is None
        ):
            raise ValueError(
                "value cannot be None when missingness is NOT_MISSING"
            )

        return self


# ============================================================================
# EVENT
# ============================================================================


class Event(IdentifiedModel):
    """
    Representation of an event believed to have occurred.

    Event existence and event interpretation are kept separate.
    """

    event_type: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)

    temporal: TemporalInterval
    spatial: SpatialReference | None = None

    source_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)

    epistemic_status: EpistemicStatus = EpistemicStatus.REPORTED
    confidence: Probability | None = None

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC


# ============================================================================
# CLAIM
# ============================================================================


class Claim(IdentifiedModel):
    """
    Atomic proposition represented by CEUTIA.

    A claim can be supported, contradicted or left unresolved.
    """

    statement: str = Field(min_length=1, max_length=5000)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    source_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)

    epistemic_status: EpistemicStatus = EpistemicStatus.UNKNOWN

    confidence: Probability | None = None

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    @model_validator(mode="after")
    def validate_confidence(self) -> Claim:
        if self.epistemic_status == EpistemicStatus.UNKNOWN and self.confidence is not None:
            raise ValueError(
                "UNKNOWN claims should not carry a resolved confidence value"
            )

        return self


# ============================================================================
# EVIDENCE
# ============================================================================


class Evidence(DomainModel):
    """
    Relationship between an evidentiary object and a claim.

    Evidence does not become stronger merely because more sources repeat it.
    Source independence must be represented explicitly.
    """

    id: UUID = Field(default_factory=uuid4)

    claim_id: UUID
    source_id: UUID

    direction: EvidenceDirection = EvidenceDirection.UNKNOWN
    quality: QualityLevel = QualityLevel.UNKNOWN

    reliability: Probability | None = None
    independence_group: str | None = None

    description: str | None = Field(default=None, max_length=5000)

    artifact_id: UUID | None = None
    observation_id: UUID | None = None

    uncertainty: MeasurementUncertainty | None = None

    @model_validator(mode="after")
    def validate_evidence_origin(self) -> Evidence:
        if self.artifact_id is None and self.observation_id is None:
            raise ValueError(
                "evidence must reference at least one artifact or observation"
            )

        return self


class EvidenceBundle(IdentifiedModel):
    """
    Group of evidence items used to evaluate a claim.

    The bundle preserves both supporting and contradictory evidence.
    """

    claim_id: UUID
    evidence_ids: list[UUID] = Field(default_factory=list)

    supporting_count: NonNegativeInt = 0
    refuting_count: NonNegativeInt = 0

    independent_source_groups: list[str] = Field(default_factory=list)

    contradiction_present: bool = False

    aggregate_confidence: Probability | None = None

    @model_validator(mode="after")
    def validate_bundle(self) -> EvidenceBundle:
        if (
            self.supporting_count == 0
            and self.refuting_count == 0
            and self.evidence_ids
        ):
            raise ValueError(
                "evidence counts cannot both be zero when evidence exists"
            )

        return self


# ============================================================================
# PROVENANCE
# ============================================================================


class ProvenanceLinkType(StrEnum):
    DERIVED_FROM = "DERIVED_FROM"
    OBSERVED_FROM = "OBSERVED_FROM"
    PUBLISHED_BY = "PUBLISHED_BY"
    CORROBORATES = "CORROBORATES"
    CONTRADICTS = "CONTRADICTS"
    INFORMS = "INFORMS"
    GENERATED_BY = "GENERATED_BY"
    VALIDATED_BY = "VALIDATED_BY"
    SUPERSEDES = "SUPERSEDES"


class ProvenanceLink(DomainModel):
    """
    Directed provenance edge between domain objects.
    """

    source_id: UUID
    target_id: UUID
    relation: ProvenanceLinkType

    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value


class ProvenanceGraph(DomainModel):
    """
    Explicit lineage graph for an analytical object.
    """

    links: list[ProvenanceLink] = Field(default_factory=list)

    root_ids: list[UUID] = Field(default_factory=list)
    terminal_ids: list[UUID] = Field(default_factory=list)


# ============================================================================
# SIGNAL
# ============================================================================


class SignalType(StrEnum):
    ANOMALY = "ANOMALY"
    TREND = "TREND"
    ACCELERATION = "ACCELERATION"
    CHANGE_POINT = "CHANGE_POINT"
    PERSISTENCE = "PERSISTENCE"
    COUPLING = "COUPLING"
    DECOUPLING = "DECOUPLING"
    SYNCHRONIZATION = "SYNCHRONIZATION"
    PROPAGATION = "PROPAGATION"
    CAPACITY_STRESS = "CAPACITY_STRESS"
    THRESHOLD_PROXIMITY = "THRESHOLD_PROXIMITY"
    CASCADE = "CASCADE"
    WEAK_SIGNAL = "WEAK_SIGNAL"
    CONTRADICTION = "CONTRADICTION"
    INFORMATION = "INFORMATION"
    UNKNOWN = "UNKNOWN"


class Signal(IdentifiedModel):
    """
    Analytical signal extracted from observations and/or evidence.

    A signal is not automatically an alert.
    """

    signal_type: SignalType
    name: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=5000)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    source_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)

    strength: Probability | None = None
    persistence: NonNegativeFloat | None = None
    uncertainty: Probability | None = None

    variables: list[str] = Field(default_factory=list)

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC


# ============================================================================
# DYNAMIC STATE
# ============================================================================


class DynamicState(IdentifiedModel):
    """
    Snapshot of a system variable or multidimensional system state.
    """

    variable: str = Field(min_length=1, max_length=300)

    value: float
    baseline: float | None = None

    rate_of_change: float | None = None
    acceleration: float | None = None

    reserve: Probability | None = None
    pressure: Probability | None = None

    temporal: TemporalInterval
    spatial: SpatialReference | None = None

    uncertainty: Probability | None = None


# ============================================================================
# CAPACITY
# ============================================================================


class CapacityState(IdentifiedModel):
    """
    Capacity representation.

    Global capacity is not necessarily effective capacity, and effective
    capacity is not necessarily accessible capacity.
    """

    subsystem: str = Field(min_length=1, max_length=300)

    global_capacity: NonNegativeFloat | None = None
    effective_capacity: NonNegativeFloat | None = None
    accessible_capacity: NonNegativeFloat | None = None

    current_load: NonNegativeFloat | None = None
    arrival_rate: NonNegativeFloat | None = None
    service_rate: NonNegativeFloat | None = None

    queue_length: NonNegativeFloat | None = None
    waiting_time: NonNegativeFloat | None = None

    utilization: NonNegativeFloat | None = None

    temporal: TemporalInterval
    spatial: SpatialReference | None = None

    @field_validator("utilization")
    @classmethod
    def validate_utilization(cls, value: float | None) -> float | None:
        if value is not None and value > 1.0:
            raise ValueError("utilization must be between 0 and 1")
        return value


# ============================================================================
# INFERENCE
# ============================================================================


class Inference(IdentifiedModel):
    """
    Explicit analytical inference.

    Inference is separated from raw observation and from hypothesis.
    """

    statement: str = Field(min_length=1, max_length=5000)

    input_ids: list[UUID] = Field(default_factory=list)

    confidence: Probability | None = None
    uncertainty: Probability | None = None

    method: str = Field(min_length=1, max_length=300)
    model_version: str | None = Field(default=None, max_length=200)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC


# ============================================================================
# HYPOTHESIS COMPETITION
# ============================================================================


class HypothesisStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPPORTED = "SUPPORTED"
    WEAKENED = "WEAKENED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    SUPERSEDED = "SUPERSEDED"


class Hypothesis(IdentifiedModel):
    """
    Falsifiable explanatory hypothesis.

    Multiple hypotheses may coexist for the same observed phenomenon.
    """

    statement: str = Field(min_length=1, max_length=5000)

    status: HypothesisStatus = HypothesisStatus.ACTIVE

    prior_probability: Probability | None = None
    posterior_probability: Probability | None = None

    supporting_evidence_ids: list[UUID] = Field(default_factory=list)
    refuting_evidence_ids: list[UUID] = Field(default_factory=list)

    discriminating_predictions: list[str] = Field(default_factory=list)

    falsification_criteria: list[str] = Field(default_factory=list)

    model_version: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_probabilities(self) -> Hypothesis:
        if (
            self.prior_probability is not None
            and self.posterior_probability is not None
        ):
            if (
                self.posterior_probability == 0.0
                and self.status == HypothesisStatus.ACTIVE
            ):
                raise ValueError(
                    "an active hypothesis cannot have zero posterior probability"
                )

        return self


class HypothesisCompetition(IdentifiedModel):
    """
    Explicit set of competing hypotheses for one analytical question.
    """

    question: str = Field(min_length=1, max_length=5000)

    hypothesis_ids: list[UUID] = Field(min_length=1)

    selected_hypothesis_id: UUID | None = None

    @model_validator(mode="after")
    def validate_selection(self) -> HypothesisCompetition:
        if (
            self.selected_hypothesis_id is not None
            and self.selected_hypothesis_id not in self.hypothesis_ids
        ):
            raise ValueError(
                "selected_hypothesis_id must belong to hypothesis_ids"
            )

        return self


# ============================================================================
# PREDICTION
# ============================================================================


class PredictionStatus(StrEnum):
    OPEN = "OPEN"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_CONFIRMED = "PARTIALLY_CONFIRMED"
    DISCONFIRMED = "DISCONFIRMED"
    EXPIRED = "EXPIRED"


class Prediction(IdentifiedModel):
    """
    Time-bounded prediction registered before its outcome is known.

    Predictions must remain available for retrospective calibration.
    """

    statement: str = Field(min_length=1, max_length=5000)

    probability: Probability

    target_time: datetime
    evaluation_window_start: datetime | None = None
    evaluation_window_end: datetime | None = None

    basis_ids: list[UUID] = Field(default_factory=list)

    model_version: str | None = Field(default=None, max_length=200)

    status: PredictionStatus = PredictionStatus.OPEN

    outcome_id: UUID | None = None

    @field_validator("target_time")
    @classmethod
    def validate_target_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("target_time must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_evaluation_window(self) -> Prediction:
        if (
            self.evaluation_window_start is not None
            and self.evaluation_window_end is not None
            and self.evaluation_window_end <= self.evaluation_window_start
        ):
            raise ValueError(
                "evaluation_window_end must be later than evaluation_window_start"
            )

        return self


# ============================================================================
# SCENARIO
# ============================================================================


class ScenarioType(StrEnum):
    BASELINE = "BASELINE"
    ADVERSE = "ADVERSE"
    FAVOURABLE = "FAVOURABLE"
    SHOCK = "SHOCK"
    CASCADE = "CASCADE"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    UNKNOWN = "UNKNOWN"


class Scenario(IdentifiedModel):
    """
    Conditional representation of a possible future system trajectory.

    A scenario is not a prediction unless explicitly represented as one.
    """

    name: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=10000)

    scenario_type: ScenarioType

    assumptions: list[str] = Field(default_factory=list)
    trigger_conditions: list[str] = Field(default_factory=list)

    probability: Probability | None = None

    horizon_start: datetime | None = None
    horizon_end: datetime | None = None

    input_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_horizon(self) -> Scenario:
        if (
            self.horizon_start is not None
            and self.horizon_end is not None
            and self.horizon_end <= self.horizon_start
        ):
            raise ValueError("horizon_end must be later than horizon_start")

        return self


# ============================================================================
# ALERT
# ============================================================================


class AlertType(StrEnum):
    HEALTH = "HEALTH"
    PSYCHOSOCIAL = "PSYCHOSOCIAL"
    VIOLENCE_ESCALATION = "VIOLENCE_ESCALATION"
    INFORMATION = "INFORMATION"
    ENVIRONMENT = "ENVIRONMENT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    INSTITUTIONAL = "INSTITUTIONAL"
    MIGRATION_HUMANITARIAN = "MIGRATION_HUMANITARIAN"
    MULTISYSTEM = "MULTISYSTEM"


class AlertLevel(StrEnum):
    LEVEL_0 = "LEVEL_0"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    LEVEL_5 = "LEVEL_5"


class AlertStatus(StrEnum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    ESCALATED = "ESCALATED"
    DISMISSED = "DISMISSED"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class Alert(IdentifiedModel):
    """
    Qualified system alert.

    CEUTIA PUBLIC generates analytical alerts.
    Human review determines whether and how an alert should be escalated.

    An alert does not itself constitute an autonomous security decision.
    """

    alert_type: AlertType
    level: AlertLevel

    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=10000)

    status: AlertStatus = AlertStatus.PROPOSED

    signal_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)
    hypothesis_ids: list[UUID] = Field(default_factory=list)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    probability: Probability | None = None
    uncertainty: Probability | None = None

    severity: NonNegativeInt | None = Field(default=None, le=5)
    urgency: NonNegativeInt | None = Field(default=None, le=5)

    human_review_required: bool = True
    human_review_completed: bool = False

    recommended_action: str | None = Field(default=None, max_length=5000)

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    @model_validator(mode="after")
    def validate_review_state(self) -> Alert:
        if self.human_review_completed and not self.human_review_required:
            return self

        if self.status in {
            AlertStatus.CONFIRMED,
            AlertStatus.ESCALATED,
        } and not self.human_review_completed:
            raise ValueError(
                "confirmed or escalated alerts require completed human review"
            )

        return self


# ============================================================================
# DECISION
# ============================================================================


class Decision(IdentifiedModel):
    """
    Human or institutionally authorized decision resulting from an alert,
    analytical finding or other evidence.

    CEUTIA records decisions; it does not silently turn analytical output
    into an autonomous institutional decision.
    """

    statement: str = Field(min_length=1, max_length=10000)

    basis_ids: list[UUID] = Field(default_factory=list)
    alert_ids: list[UUID] = Field(default_factory=list)

    decision_maker: str = Field(min_length=1, max_length=500)

    decision_time: datetime

    rationale: str | None = Field(default=None, max_length=10000)

    @field_validator("decision_time")
    @classmethod
    def validate_decision_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("decision_time must be timezone-aware")
        return value


# ============================================================================
# OUTCOME
# ============================================================================


class Outcome(IdentifiedModel):
    """
    Observed result used to evaluate predictions and decisions.
    """

    description: str = Field(min_length=1, max_length=10000)

    observed_at: datetime

    source_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)

    matches_prediction: bool | None = None

    evaluation_confidence: Probability | None = None

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value


# ============================================================================
# MODEL / ANALYTICAL LINEAGE
# ============================================================================


class ModelExecution(IdentifiedModel):
    """
    Record of an analytical model execution.

    The execution record is required for reproducibility and retrospective
    evaluation of predictions.
    """

    model_name: str = Field(min_length=1, max_length=300)
    model_version: str = Field(min_length=1, max_length=200)

    input_ids: list[UUID] = Field(default_factory=list)
    output_ids: list[UUID] = Field(default_factory=list)

    executed_at: datetime

    code_version: str | None = Field(default=None, max_length=200)
    configuration_hash: str | None = Field(default=None, max_length=256)

    deterministic: bool = False

    @field_validator("executed_at")
    @classmethod
    def validate_executed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("executed_at must be timezone-aware")
        return value


# ============================================================================
# PERSON / SYSTEM SEPARATION
# ============================================================================


class AnalyticalSubject(StrEnum):
    SYSTEM = "SYSTEM"
    AGGREGATE = "AGGREGATE"
    PERSON = "PERSON"


class PersonSystemBoundary(DomainModel):
    """
    Explicit declaration of the analytical boundary of an object.

    Person-level information must not silently enter territorial/system
    intelligence as an identifiable individual-level signal.
    """

    subject: AnalyticalSubject

    privacy_preserving_aggregation: bool = False

    aggregation_group: str | None = None

    @model_validator(mode="after")
    def validate_boundary(self) -> PersonSystemBoundary:
        if (
            self.subject == AnalyticalSubject.SYSTEM
            and self.privacy_preserving_aggregation
        ):
            raise ValueError(
                "system-level objects cannot declare person aggregation"
            )

        if self.subject == AnalyticalSubject.AGGREGATE:
            if not self.privacy_preserving_aggregation:
                raise ValueError(
                    "aggregate analytical objects require privacy-preserving "
                    "aggregation to be explicitly declared"
                )

            if not self.aggregation_group:
                raise ValueError(
                    "aggregate objects require an aggregation_group"
                )

        return self


# ============================================================================
# UNKNOWN / DATA QUALITY
# ============================================================================


class DataQualityGate(StrEnum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_WARNING = "ACCEPT_WITH_WARNING"
    QUARANTINE = "QUARANTINE"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class DataQualityAssessment(DomainModel):
    """
    Quality gate applied before information enters analytical processing.
    """

    gate: DataQualityGate

    completeness: Probability | None = None
    consistency: Probability | None = None
    validity: Probability | None = None
    timeliness: Probability | None = None

    issues: list[str] = Field(default_factory=list)

    assessed_at: datetime

    @field_validator("assessed_at")
    @classmethod
    def validate_assessed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("assessed_at must be timezone-aware")
        return value


# ============================================================================
# CANONICAL DOMAIN ENVELOPE
# ============================================================================


class EpistemicObjectType(StrEnum):
    SOURCE = "SOURCE"
    ARTIFACT = "ARTIFACT"
    OBSERVATION = "OBSERVATION"
    EVENT = "EVENT"
    CLAIM = "CLAIM"
    EVIDENCE = "EVIDENCE"
    EVIDENCE_BUNDLE = "EVIDENCE_BUNDLE"
    SIGNAL = "SIGNAL"
    DYNAMIC_STATE = "DYNAMIC_STATE"
    CAPACITY_STATE = "CAPACITY_STATE"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    PREDICTION = "PREDICTION"
    SCENARIO = "SCENARIO"
    ALERT = "ALERT"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"


class EpistemicEnvelope(IdentifiedModel):
    """
    Lightweight canonical envelope for cross-layer references.

    The envelope allows pipelines to refer to heterogeneous epistemic
    objects without collapsing their semantic distinctions.
    """

    object_type: EpistemicObjectType
    object_id: UUID

    epistemic_status: EpistemicStatus = EpistemicStatus.UNKNOWN

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC
    subject_class: DataSubjectClass = DataSubjectClass.UNKNOWN

    provenance_ids: list[UUID] = Field(default_factory=list)

    uncertainty: Probability | None = None

    version: PositiveInt = 1


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================


__all__ = [
    "Alert",
    "AlertLevel",
    "AlertStatus",
    "AlertType",
    "AnalyticalSubject",
    "Artifact",
    "CapacityState",
    "Claim",
    "DataQualityAssessment",
    "DataQualityGate",
    "DataSubjectClass",
    "Decision",
    "DomainModel",
    "DynamicState",
    "EpistemicEnvelope",
    "EpistemicObjectType",
    "EpistemicStatus",
    "Evidence",
    "EvidenceBundle",
    "EvidenceDirection",
    "Event",
    "Hypothesis",
    "HypothesisCompetition",
    "HypothesisStatus",
    "Inference",
    "MeasurementUncertainty",
    "MissingnessMechanism",
    "ModelExecution",
    "Observation",
    "Outcome",
    "PersonSystemBoundary",
    "Prediction",
    "PredictionStatus",
    "ProvenanceGraph",
    "ProvenanceLink",
    "ProvenanceLinkType",
    "QualityLevel",
    "Scenario",
    "ScenarioType",
    "SensitivityClass",
    "Signal",
    "SignalType",
    "Source",
    "SourceAuthenticity",
    "SourceType",
    "SpatialReference",
    "TemporalInterval",
]