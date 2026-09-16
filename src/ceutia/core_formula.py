"""
CeutIA - Fórmula Maestra de Susceptibilidad Sistémica y Riesgo Trazable
Ruta: src/ceutia/core_formula.py
"""

from __future__ import annotations
from typing import Any, Dict, Tuple

import numpy as np
from pydantic import BaseModel, Field, field_validator


class SystemicVariables(BaseModel):
    """Variables fundamentales para el cálculo de susceptibilidad sistémica."""

    shock_magnitude: float = Field(..., ge=0.0, description="Magnitud del choque o perturbación exógena.")
    sensitivity: float = Field(..., ge=0.0, le=1.0, description="Sensibilidad local del territorio.")
    adaptive_reserve: float = Field(..., ge=0.0, description="Reserva adaptativa disponible C(t) - L(t).")
    coupling_index: float = Field(..., ge=0.0, le=1.0, description="Grado de acoplamiento de la red.")
    propagation_rate: float = Field(..., ge=0.0, description="Velocidad de propagación de la perturbación.")
    confidence_interval: Tuple[float, float] = Field(..., description="Intervalo de confianza estadístico [min, max].")

    @field_validator("confidence_interval")
    @classmethod
    def validate_ci(cls, value: Tuple[float, float]) -> Tuple[float, float]:
        if value[0] > value[1]:
            raise ValueError("El límite inferior del intervalo de confianza no puede superar al superior.")
        return value


class MasterSusceptibilityEngine:
    """Implementación de la fórmula integral de susceptibilidad y riesgo sistémico."""

    @staticmethod
    def compute_systemic_susceptibility(vars: SystemicVariables) -> Dict[str, Any]:
        """
        Calcula el índice de susceptibilidad sistémica mediante la interacción de orden superior:
        Susceptibilidad = Shock * Sensibilidad * Reserva^(-1) * Acoplamiento * Propagación.
        """
        reserve_inverse = 1.0 / (vars.adaptive_reserve + 1e-9)
        raw_susceptibility = (
            vars.shock_magnitude
            * vars.sensitivity
            * reserve_inverse
            * vars.coupling_index
            * vars.propagation_rate
        )

        normalized_risk = float(np.clip(raw_susceptibility, 0.0, 1.0))
        ci_width = vars.confidence_interval[1] - vars.confidence_interval[0]
        uncertainty_factor = float(ci_width * vars.sensitivity * reserve_inverse)

        return {
            "systemic_susceptibility_index": normalized_risk,
            "uncertainty_propagation": uncertainty_factor,
            "critical_threshold_exceeded": normalized_risk > 0.85,
            "human_oversight_required": True,
            "coercive_action_permitted": False,
        }
