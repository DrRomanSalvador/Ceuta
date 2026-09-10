from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class EpistemicStatus(str, Enum):
    HYPOTHESIS_UNCALIBRATED = "HYPOTHESIS_UNCALIBRATED"
    BLOCKED = "BLOCKED"
    PROXY_RISK = "PROXY_RISK"


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
