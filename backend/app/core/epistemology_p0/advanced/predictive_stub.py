"""
P2 — Esqueleto de consumidor predictivo acotado.

NO es un modelo de producción ni afirma causalidad.
Demuestra el contrato: solo Observation con peso, nunca escalares desnudos.
La predicción queda marcada como HYPOTHESIS / UNVERIFIED.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
import math

from ..contracts.ceutia_serpiente import Observation
from ..epistemology.states import EpistemicStatus


@dataclass
class PredictionRequest:
    target_variable: str
    horizon_steps: int
    observations: List[Observation]
    geography: Optional[str] = None


@dataclass
class PredictionResult:
    target_variable: str
    horizon_steps: int
    point_estimate: Optional[float]
    interval_lower: Optional[float]
    interval_upper: Optional[float]
    epistemic_status: str
    mean_input_weight: float
    n_observations_used: int
    method: str
    explanation: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "target_variable": self.target_variable,
            "horizon_steps": self.horizon_steps,
            "point_estimate": self.point_estimate,
            "interval_lower": self.interval_lower,
            "interval_upper": self.interval_upper,
            "epistemic_status": self.epistemic_status,
            "mean_input_weight": self.mean_input_weight,
            "n_observations_used": self.n_observations_used,
            "method": self.method,
            "explanation": self.explanation,
            "created_at": self.created_at,
            "disclaimer": (
                "UNVERIFIED hypothesis. Not a causal claim. "
                "Requires human review before operational use."
            ),
        }


class PredictiveConsumerStub:
    """
    Media ponderada naive + intervalo por dispersión de pesos.
    Solo acepta Observation; rechaza valores sueltos.
    """

    def predict(self, request: PredictionRequest) -> PredictionResult:
        if request.horizon_steps < 1:
            raise ValueError("horizon_steps must be >= 1")
        if not request.observations:
            return PredictionResult(
                target_variable=request.target_variable,
                horizon_steps=request.horizon_steps,
                point_estimate=None,
                interval_lower=None,
                interval_upper=None,
                epistemic_status=EpistemicStatus.UNKNOWN.value,
                mean_input_weight=0.0,
                n_observations_used=0,
                method="weighted_mean_stub",
                explanation="No observations provided.",
            )

        values: List[float] = []
        weights: List[float] = []
        for obs in request.observations:
            if not isinstance(obs, Observation):
                raise TypeError("only Observation instances allowed (no naked scalars)")
            if obs.semantic_definition is None or not str(obs.semantic_definition).strip():
                raise ValueError("observation missing semantic_definition")
            try:
                v = float(obs.value)
            except (TypeError, ValueError):
                continue
            w = max(0.0, min(1.0, float(obs.confidence) * (1.0 - 0.7 * float(obs.source_dependence_ratio))))
            values.append(v)
            weights.append(w)

        if not values:
            return PredictionResult(
                target_variable=request.target_variable,
                horizon_steps=request.horizon_steps,
                point_estimate=None,
                interval_lower=None,
                interval_upper=None,
                epistemic_status=EpistemicStatus.UNKNOWN.value,
                mean_input_weight=0.0,
                n_observations_used=0,
                method="weighted_mean_stub",
                explanation="No numeric values usable.",
            )

        wsum = sum(weights) or 1e-9
        point = sum(v * w for v, w in zip(values, weights)) / wsum
        mean_w = sum(weights) / len(weights)
        # dispersión simple
        var = sum(w * (v - point) ** 2 for v, w in zip(values, weights)) / wsum
        std = math.sqrt(max(0.0, var))
        # horizonte ensancha el intervalo (heurística, no modelo calibrado)
        widen = 1.0 + 0.1 * (request.horizon_steps - 1)
        half = std * widen + (1.0 - mean_w) * abs(point) * 0.05

        status = EpistemicStatus.HYPOTHESIS.value
        if mean_w < 0.3:
            status = EpistemicStatus.UNVERIFIED.value

        return PredictionResult(
            target_variable=request.target_variable,
            horizon_steps=request.horizon_steps,
            point_estimate=round(point, 6),
            interval_lower=round(point - half, 6),
            interval_upper=round(point + half, 6),
            epistemic_status=status,
            mean_input_weight=round(mean_w, 6),
            n_observations_used=len(values),
            method="weighted_mean_stub",
            explanation=(
                "Heuristic weighted mean of Observations. "
                "Not calibrated. Not causal. Human review required."
            ),
        )
