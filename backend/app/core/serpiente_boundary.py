from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from pydantic import BaseModel, Field, field_validator


class SerpientePredictionEnvelope(BaseModel):
    schema_version: str = Field(min_length=1)
    prediction_id: str = Field(min_length=1)
    origin_time: datetime
    horizon: str = Field(min_length=1)
    target: str = Field(min_length=1)
    probability: float = Field(ge=0.0, le=1.0)
    lower: float
    upper: float
    uncertainty: dict[str, float]
    model_disagreement: float = Field(ge=0.0, le=1.0)
    regime: str = Field(min_length=1)
    provenance: list[str] = Field(min_length=1)
    point_in_time_fingerprint: str = Field(min_length=64, max_length=64)
    alert_ids: list[str] = Field(default_factory=list)

    @field_validator("probability", "lower", "upper", "model_disagreement")
    @classmethod
    def finite(cls, value: float) -> float:
        if not isfinite(value):
            raise ValueError("SERPIENTE prediction values must be finite")
        return value

    @field_validator("uncertainty")
    @classmethod
    def uncertainty_finite(cls, value: dict[str, float]) -> dict[str, float]:
        if not value or any(not isfinite(v) or v < 0 for v in value.values()):
            raise ValueError("SERPIENTE uncertainty must contain finite non-negative values")
        return value

    def validate_at(self, decision_time: datetime) -> None:
        if self.origin_time.tzinfo is None or decision_time.tzinfo is None:
            raise ValueError("prediction and decision time must be timezone-aware")
        if self.origin_time.astimezone(timezone.utc) > decision_time.astimezone(timezone.utc):
            raise ValueError("SERPIENTE prediction is from the future relative to decision time")
        if self.lower > self.upper:
            raise ValueError("SERPIENTE prediction interval is invalid")
