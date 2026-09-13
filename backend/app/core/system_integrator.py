from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite, sqrt
from statistics import mean
from typing import Sequence


class EpistemicStatus(str, Enum):
    HYPOTHESIS_UNCALIBRATED = "HYPOTHESIS_UNCALIBRATED"
    BLOCKED = "BLOCKED"
    PROXY_RISK = "PROXY_RISK"


@dataclass(frozen=True, slots=True)
class ProxyGateAssessment:
    """Auditable screening result for spatial-composition proxy risk.

    This is an association screen, not a causal or predictive model. A positive
    result blocks operational promotion; a negative result does not establish
    safety or causal validity.
    """

    status: EpistemicStatus
    sample_size: int
    signal_composition_association: float | None
    signal_outcome_association: float | None
    signal_outcome_partial_association: float | None
    method: str
    explanation: str


@dataclass(frozen=True, slots=True)
class SystemView:
    local_vulnerability: float
    cascade_potential: float
    epistemic_status: EpistemicStatus
    proxy_gate_result: str


def _clamp01(value: float) -> float:
    if not isfinite(value):
        raise ValueError("value must be finite")
    return max(0.0, min(1.0, value))


def _as_finite_vector(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result:
        raise ValueError(f"{name} must not be empty")
    if any(not isfinite(value) for value in result):
        raise ValueError(f"{name} must contain only finite values")
    return result


def _pearson(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("vectors must have equal length and at least two observations")
    x_mean = mean(x)
    y_mean = mean(y)
    dx = tuple(value - x_mean for value in x)
    dy = tuple(value - y_mean for value in y)
    xx = sum(value * value for value in dx)
    yy = sum(value * value for value in dy)
    if xx == 0.0 or yy == 0.0:
        raise ValueError("correlation is undefined for a constant vector")
    return sum(a * b for a, b in zip(dx, dy)) / sqrt(xx * yy)


def _residualize(values: Sequence[float], control: Sequence[float]) -> tuple[float, ...]:
    control_mean = mean(control)
    value_mean = mean(values)
    centered_control = tuple(value - control_mean for value in control)
    centered_values = tuple(value - value_mean for value in values)
    denominator = sum(value * value for value in centered_control)
    if denominator == 0.0:
        raise ValueError("partial correlation is undefined for a constant control")
    beta = sum(v * c for v, c in zip(centered_values, centered_control)) / denominator
    intercept = value_mean - beta * control_mean
    return tuple(value - (intercept + beta * c) for value, c in zip(values, control))


def partial_correlation(
    signal: Sequence[float],
    outcome: Sequence[float],
    control: Sequence[float],
) -> float:
    """Return Pearson partial correlation of signal and outcome controlling for one variable."""
    signal_values = _as_finite_vector(signal, name="signal")
    outcome_values = _as_finite_vector(outcome, name="outcome")
    control_values = _as_finite_vector(control, name="control")
    if not (len(signal_values) == len(outcome_values) == len(control_values)):
        raise ValueError("signal, outcome and control must have equal length")
    return _pearson(
        _residualize(signal_values, control_values),
        _residualize(outcome_values, control_values),
    )


def evaluate_spatial_proxy_gate(
    *,
    signal: Sequence[float],
    composition: Sequence[float],
    outcome: Sequence[float],
    minimum_sample_size: int = 10,
) -> ProxyGateAssessment:
    """Screen a spatial signal for geographic-composition proxy risk.

    The gate compares absolute association strengths. It deliberately does not
    infer intent, causality, discrimination, or safety. Insufficient data blocks
    operational use and returns ``BLOCKED``.
    """
    if minimum_sample_size < 3:
        raise ValueError("minimum_sample_size must be at least 3")

    signal_values = _as_finite_vector(signal, name="signal")
    composition_values = _as_finite_vector(composition, name="composition")
    outcome_values = _as_finite_vector(outcome, name="outcome")

    sample_size = len(signal_values)
    if not (len(composition_values) == sample_size == len(outcome_values)):
        raise ValueError("signal, composition and outcome must have equal length")

    if sample_size < minimum_sample_size:
        return ProxyGateAssessment(
            status=EpistemicStatus.BLOCKED,
            sample_size=sample_size,
            signal_composition_association=None,
            signal_outcome_association=None,
            signal_outcome_partial_association=None,
            method="pearson_screening_plus_partial_correlation",
            explanation="NO_VERIFICADO: insufficient observations for proxy screening",
        )

    try:
        signal_composition = _pearson(signal_values, composition_values)
        signal_outcome = _pearson(signal_values, outcome_values)
    except ValueError as exc:
        return ProxyGateAssessment(
            status=EpistemicStatus.BLOCKED,
            sample_size=sample_size,
            signal_composition_association=None,
            signal_outcome_association=None,
            signal_outcome_partial_association=None,
            method="pearson_screening_plus_partial_correlation",
            explanation=f"NO_VERIFICADO: association screening undefined: {exc}",
        )

    try:
        partial = partial_correlation(
            signal_values,
            outcome_values,
            composition_values,
        )
        partial_explanation = ""
    except ValueError as exc:
        partial = None
        partial_explanation = (
            f" Partial association unavailable: {exc}."
        )

    composition_strength = abs(signal_composition)
    outcome_strength = abs(signal_outcome)
    partial_strength = abs(partial) if partial is not None else None

    composition_exceeds_outcome = composition_strength > outcome_strength
    composition_exceeds_partial = (
        partial_strength is not None
        and composition_strength > partial_strength
    )

    if composition_exceeds_outcome or composition_exceeds_partial:
        status = EpistemicStatus.PROXY_RISK
        explanation = (
            "PROXY_RISK: signal-composition association is stronger than the "
            "signal-outcome association or its composition-controlled association; "
            "the signal is not operationally promotable without human review."
            + partial_explanation
        )
    else:
        status = EpistemicStatus.HYPOTHESIS_UNCALIBRATED
        explanation = (
            "OK: this screening gate did not identify stronger composition association. "
            "This does not establish causal validity, absence of bias, or operational safety."
            + partial_explanation
        )

    return ProxyGateAssessment(
        status=status,
        sample_size=sample_size,
        signal_composition_association=round(signal_composition, 6),
        signal_outcome_association=round(signal_outcome, 6),
        signal_outcome_partial_association=(
            round(partial, 6) if partial is not None else None
        ),
        method="pearson_screening_plus_partial_correlation",
        explanation=explanation,
    )


def compose_local_vulnerability(*, capacity: float, load: float, sensitivity: float):
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    if load < 0:
        raise ValueError("load must not be negative")
    sensitivity = _clamp01(sensitivity)
    pressure = _clamp01(load / capacity)
    vulnerability = _clamp01(pressure * (0.5 + 0.5 * sensitivity))
    return vulnerability, EpistemicStatus.HYPOTHESIS_UNCALIBRATED, "UNVERIFICADO"


def compose_cascade_potential(*, coupling: float, propagation: float, local_vulnerability: float):
    coupling = _clamp01(coupling)
    propagation = _clamp01(propagation)
    local_vulnerability = _clamp01(local_vulnerability)
    potential = _clamp01(coupling * propagation * local_vulnerability)
    return potential, EpistemicStatus.HYPOTHESIS_UNCALIBRATED, "UNVERIFICADO"


def proxy_gate_tension_signal(*, signal_predicts_composition_stronger_than_outcome: bool | None, data_sufficient: bool):
    if not data_sufficient or signal_predicts_composition_stronger_than_outcome is None:
        return "NO_VERIFICADO: proxy gate blocked by insufficient outcome data", EpistemicStatus.BLOCKED
    if signal_predicts_composition_stronger_than_outcome:
        return "PROXY_RISK: composition signal is stronger than validated outcome", EpistemicStatus.PROXY_RISK
    return "OK: proxy relationship not supported", EpistemicStatus.HYPOTHESIS_UNCALIBRATED


def build_system_view(*, capacity: float, load: float, tension_signal_present: bool, tension_predicts_composition_stronger: bool | None, composition_outcome_data_sufficient: bool):
    vulnerability, _, _ = compose_local_vulnerability(capacity=capacity, load=load, sensitivity=0.5)
    cascade, _, _ = compose_cascade_potential(coupling=0.5, propagation=0.5, local_vulnerability=vulnerability)
    if tension_signal_present:
        proxy_result, proxy_status = proxy_gate_tension_signal(
            signal_predicts_composition_stronger_than_outcome=tension_predicts_composition_stronger,
            data_sufficient=composition_outcome_data_sufficient,
        )
        return SystemView(vulnerability, cascade, proxy_status, proxy_result)
    return SystemView(vulnerability, cascade, EpistemicStatus.HYPOTHESIS_UNCALIBRATED, "NO_VERIFICADO: no tension proxy evaluated")

# This module intentionally has no side effects and does not ingest data or emit operational risk.
