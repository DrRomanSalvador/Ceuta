from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ForecastModel(Protocol):
    model_id: str
    def predict(self, features: tuple[float, ...]) -> float: ...


@dataclass(frozen=True, slots=True)
class ModelForecast:
    model_id: str
    point: float


@dataclass(frozen=True, slots=True)
class EnsembleForecast:
    point: float
    members: tuple[ModelForecast, ...]
    disagreement: float


class MultimodelForecaster:
    def forecast(self, models: tuple[ForecastModel, ...], features: tuple[float, ...]) -> EnsembleForecast:
        if not models:
            raise ValueError("at least one model is required")
        members = tuple(ModelForecast(m.model_id, float(m.predict(features))) for m in models)
        point = sum(m.point for m in members) / len(members)
        disagreement = sum(abs(m.point - point) for m in members) / len(members)
        return EnsembleForecast(point, members, disagreement)
