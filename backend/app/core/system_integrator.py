"""
CeutIA — System Integrator (skeleton, non-operational)
Status: SKELETON / HYPOTHESIS / NOT CALIBRATED / NOT OPERATIONAL
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class EpistemicStatus(str, Enum):
    HYPOTHESIS_UNCALIBRATED = "hypothesis_uncalibrated"
    DESCRIPTIVE_ONLY = "descriptive_only"
    PROXY_RISK = "proxy_risk"
    NO_VERIFICADO = "no_verificado"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SystemView:
    timestamp_label: str
    components: Mapping[str, float]
    epistemic_status: EpistemicStatus
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    proxy_gate_result: str
    notes: str = ""


def _safe_float(x: Any, default: float = float("nan")) -> float:
    try:
        v = float(x)
        if v != v:
            return default
        return v
    except (TypeError, ValueError):
        return default


def compose_local_vulnerability(
    *,
    capacity: float,
    load: float,
    sensitivity: float = 0.0,
) -> tuple[float, EpistemicStatus, tuple[str, ...]]:
    import math

    cap = _safe_float(capacity)
    ld = _safe_float(load)
    sens = max(0.0, min(1.0, _safe_float(sensitivity, 0.0)))
    if cap != cap or ld != ld:
        return float("nan"), EpistemicStatus.NO_VERIFICADO, ("capacity or load not finite",)

    reserve = cap - ld
    reserve_term = 1.0 / (1.0 + math.exp(reserve / max(abs(cap), 1e-9)))
    vuln = min(1.0, max(0.0, reserve_term * (0.5 + 0.5 * sens)))
    return (
        float(vuln),
        EpistemicStatus.HYPOTHESIS_UNCALIBRATED,
        (
            "Uses static C-L only; ignores trajectory and recovery dynamics.",
            "Exponential map is a convenience, not a fitted model.",
            "No empirical calibration on Ceuta data.",
        ),
    )


def compose_cascade_potential(
    *,
    coupling: float,
    propagation: float,
    local_vulnerability: float,
) -> tuple[float, EpistemicStatus, tuple[str, ...]]:
    c = max(0.0, _safe_float(coupling, 0.0))
    p = max(0.0, _safe_float(propagation, 0.0))
    v = max(0.0, min(1.0, _safe_float(local_vulnerability, 0.0)))
    potential = min(1.0, v * c * p)
    return (
        float(potential),
        EpistemicStatus.HYPOTHESIS_UNCALIBRATED,
        (
            "Multiplicative form cannot represent percolation / branching thresholds.",
            "Not calibrated; must not drive OWNER decisions.",
        ),
    )


def proxy_gate_tension_signal(
    *,
    signal_predicts_composition_stronger_than_outcome: bool | None,
    data_sufficient: bool,
) -> tuple[str, EpistemicStatus]:
    if not data_sufficient or signal_predicts_composition_stronger_than_outcome is None:
        return "NO_VERIFICADO — insufficient data for disparate-impact test", EpistemicStatus.BLOCKED
    if signal_predicts_composition_stronger_than_outcome:
        return "PROXY_RISK — signal predicts composition more strongly than target outcome", EpistemicStatus.PROXY_RISK
    return "PASS — no evidence of stronger composition prediction", EpistemicStatus.DESCRIPTIVE_ONLY


def build_system_view(
    *,
    capacity: float,
    load: float,
    sensitivity: float = 0.0,
    coupling: float = 0.0,
    propagation: float = 0.0,
    tension_signal_present: bool = False,
    tension_predicts_composition_stronger: bool | None = None,
    composition_outcome_data_sufficient: bool = False,
    timestamp_label: str = "unspecified",
) -> SystemView:
    vuln, vuln_status, vuln_assumptions = compose_local_vulnerability(
        capacity=capacity, load=load, sensitivity=sensitivity
    )
    casc, casc_status, casc_assumptions = compose_cascade_potential(
        coupling=coupling, propagation=propagation, local_vulnerability=vuln
    )

    if tension_signal_present:
        gate_msg, gate_status = proxy_gate_tension_signal(
            signal_predicts_composition_stronger_than_outcome=tension_predicts_composition_stronger,
            data_sufficient=composition_outcome_data_sufficient,
        )
    else:
        gate_msg, gate_status = "no tension signal supplied", EpistemicStatus.DESCRIPTIVE_ONLY

    statuses = {vuln_status, casc_status, gate_status}
    if EpistemicStatus.BLOCKED in statuses or EpistemicStatus.PROXY_RISK in statuses:
        overall = EpistemicStatus.BLOCKED
    elif EpistemicStatus.NO_VERIFICADO in statuses:
        overall = EpistemicStatus.NO_VERIFICADO
    else:
        overall = EpistemicStatus.HYPOTHESIS_UNCALIBRATED

    return SystemView(
        timestamp_label=timestamp_label,
        components={
            "local_vulnerability_sketch": vuln,
            "cascade_potential_sketch": casc,
            "capacity": float(capacity),
            "load": float(load),
            "sensitivity": float(sensitivity),
            "coupling": float(coupling),
            "propagation": float(propagation),
        },
        epistemic_status=overall,
        assumptions=vuln_assumptions + casc_assumptions,
        limitations=(
            "No official Ceuta data feeds are connected in this repository.",
            "No empirical calibration has been performed.",
            "metrics.py core is not yet importable; this skeleton does not call it.",
            "Output must not be promoted to OWNER or PUBLIC without human review and proxy gate PASS.",
        ),
        proxy_gate_result=gate_msg,
        notes="Skeleton integrator only. See docs/CEUTIA_MASTER_IMPLEMENTATION_SPECIFICATION.md.",
    )
