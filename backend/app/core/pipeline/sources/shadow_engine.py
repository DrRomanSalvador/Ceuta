from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import datetime
from math import isfinite
from typing import Protocol
from uuid import uuid4

from app.core.epistemology_p0.advanced import Forecast, Observation


class TemporalLeakageError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ShadowLedgerRecord:
    record_id: str
    forecast_id: str
    model_version: str
    variable: str
    target_time: datetime
    cutoff_time: datetime
    point: float
    status: str
    created_at: datetime

    def __post_init__(self) -> None:
        for name in ("target_time", "cutoff_time", "created_at"):
            value = getattr(self, name)
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.target_time < self.cutoff_time:
            raise ValueError("target_time cannot precede cutoff_time")
        if not isfinite(float(self.point)):
            raise ValueError("point must be finite")
        if self.status != "SHADOW_EVALUATION":
            raise ValueError("shadow records must remain SHADOW_EVALUATION")


class ShadowForecastFunction(Protocol):
    def __call__(self, observations: tuple[Observation, ...], *, cutoff_time: datetime) -> Forecast:
        ...


class ShadowLedger:
    def __init__(self) -> None:
        self._records: list[ShadowLedgerRecord] = []

    def append(self, record: ShadowLedgerRecord) -> None:
        self._records.append(record)

    @property
    def records(self) -> tuple[ShadowLedgerRecord, ...]:
        return tuple(self._records)


@dataclass(frozen=True, slots=True)
class ShadowExecutionResult:
    forecast: Forecast
    record: ShadowLedgerRecord

    @property
    def forecast_id(self) -> str:
        return self.forecast.forecast_id


class ShadowEngine:
    def __init__(self, *, model_version: str = "shadow-v1", ledger: ShadowLedger | None = None) -> None:
        if not model_version:
            raise ValueError("model_version must not be empty")
        self._model_version = model_version
        self._ledger = ledger or ShadowLedger()

    @property
    def ledger(self) -> ShadowLedger:
        return self._ledger

    @staticmethod
    def validate_temporal_boundary(observation: Observation) -> None:
        if observation.event_time.tzinfo is None or observation.event_time.utcoffset() is None:
            raise TemporalLeakageError("event_time must be timezone-aware")
        if observation.available_at.tzinfo is None or observation.available_at.utcoffset() is None:
            raise TemporalLeakageError("available_at must be timezone-aware")
        if observation.available_at < observation.event_time:
            raise TemporalLeakageError("available_at cannot precede event_time")

    def execute(
        self,
        observations: Iterable[Observation],
        *,
        cutoff_time: datetime,
        forecast_fn: ShadowForecastFunction,
    ) -> ShadowExecutionResult:
        if cutoff_time.tzinfo is None or cutoff_time.utcoffset() is None:
            raise TemporalLeakageError("cutoff_time must be timezone-aware")
        materialized = tuple(observations)
        for observation in materialized:
            self.validate_temporal_boundary(observation)
        eligible = tuple(item for item in materialized if item.available_at <= cutoff_time)
        forecast = forecast_fn(eligible, cutoff_time=cutoff_time)
        if forecast.cutoff_time != cutoff_time:
            raise TemporalLeakageError("forecast cutoff_time does not match execution cutoff")
        if forecast.target_time < cutoff_time:
            raise TemporalLeakageError("forecast target precedes cutoff")
        if forecast.status not in {"SHADOW_EVALUATION", "UNVERIFIED"}:
            raise PermissionError("shadow engine cannot persist production forecast status")
        shadow_forecast = replace(forecast, status="SHADOW_EVALUATION")
        record = ShadowLedgerRecord(
            record_id=str(uuid4()),
            forecast_id=shadow_forecast.forecast_id,
            model_version=self._model_version,
            variable=shadow_forecast.variable,
            target_time=shadow_forecast.target_time,
            cutoff_time=cutoff_time,
            point=float(shadow_forecast.point),
            status="SHADOW_EVALUATION",
            created_at=cutoff_time,
        )
        self._ledger.append(record)
        return ShadowExecutionResult(forecast=shadow_forecast, record=record)

    @property
    def production_mutation_supported(self) -> bool:
        return False
