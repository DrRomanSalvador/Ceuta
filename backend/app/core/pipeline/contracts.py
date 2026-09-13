"""Strict contracts shared by the CeutIA event-driven pipeline.

The contracts in this module are deliberately small and transport-agnostic.
They define the minimum information required to move evidence through the
pipeline without weakening temporal integrity, provenance, or validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class PipelineEvent:
    """Envelope used by the asynchronous event bus.

    ``payload`` is intentionally transport-level and may be any object, but
    stage boundaries must exchange the typed contracts defined below rather
    than unvalidated dictionaries.
    """

    event_id: str
    event_type: str
    created_at: datetime
    correlation_id: str
    source_stage: str
    schema_version: str
    payload: Any

    def __post_init__(self) -> None:
        _require_aware(self.created_at, "created_at")
        for name in (
            "event_id",
            "event_type",
            "correlation_id",
            "source_stage",
            "schema_version",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class ObservationRecord:
    """Canonical observation entering the evidence/state pipeline."""

    observation_id: str
    variable: str
    value: float
    unit: str | None
    event_time: datetime
    available_at: datetime
    source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    domain: str
    quality: float
    provenance_hash: str

    def __post_init__(self) -> None:
        for name in (
            "observation_id",
            "variable",
            "domain",
            "provenance_hash",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} must not be empty")
        if not isfinite(float(self.value)):
            raise ValueError("value must be finite")
        _require_aware(self.event_time, "event_time")
        _require_aware(self.available_at, "available_at")
        if self.available_at < self.event_time:
            raise ValueError("available_at cannot precede event_time")
        if not self.source_ids:
            raise ValueError("at least one source_id is required")
        if not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Prospective forecast-validation result.

    A report is evidence about model performance, not evidence about the
    underlying world. The calibration gate therefore treats malformed or
    incomplete mathematical inputs as failures rather than silently passing.
    """

    variable: str
    sample_size: int
    mae: float
    mse: float
    bias: float
    interval_coverage: float | None
    baseline_mse: float | None
    degradation_ratio: float | None
    passed: bool
    reason: str

    def __post_init__(self) -> None:
        if not self.variable:
            raise ValueError("variable must not be empty")
        if self.sample_size < 0:
            raise ValueError("sample_size must be non-negative")
        for name in ("mae", "mse", "bias"):
            value = float(getattr(self, name))
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
            if name in {"mae", "mse"} and value < 0.0:
                raise ValueError(f"{name} must be non-negative")
        if self.interval_coverage is not None and not 0.0 <= self.interval_coverage <= 1.0:
            raise ValueError("interval_coverage must be between 0 and 1")
        if self.baseline_mse is not None:
            if not isfinite(self.baseline_mse) or self.baseline_mse < 0.0:
                raise ValueError("baseline_mse must be finite and non-negative")
        if self.degradation_ratio is not None:
            if not isfinite(self.degradation_ratio) or self.degradation_ratio < 0.0:
                raise ValueError("degradation_ratio must be finite and non-negative")
        if not isinstance(self.passed, bool):
            raise ValueError("passed must be a boolean")
        if not self.reason:
            raise ValueError("reason must not be empty")
