"""Executable reproducibility, calibration, and scientific-boundary primitives.

This module complements ``scientific_capability``. It records enough metadata to
reconstruct a scientific computation and provides deterministic calibration and
reliability summaries without implying scientific or prospective validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
import json
import math
from typing import Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScientificExecutionState(StrEnum):
    EXECUTED = "EXECUTED"
    NOT_EXECUTED = "NOT_EXECUTED"
    REPRODUCIBILITY_INCOMPLETE = "REPRODUCIBILITY_INCOMPLETE"


class ScientificBoundary(StrEnum):
    PREDICTIVE = "PREDICTIVE"
    ASSOCIATIONAL = "ASSOCIATIONAL"
    CAUSAL = "CAUSAL"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"
    DECISION_SUPPORT = "DECISION_SUPPORT"
    SIMULATION = "SIMULATION"
    DIGITAL_TWIN = "DIGITAL_TWIN"


class ScientificExecutionRecord(BaseModel):
    """Immutable provenance for one scientific computation."""

    model_config = ConfigDict(extra="forbid")

    execution_id: str = Field(min_length=1)
    capability_id: str = Field(min_length=1)
    execution_state: ScientificExecutionState
    epistemic_boundary: ScientificBoundary
    input_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    model_version: str = Field(min_length=1)
    data_vintage: str = Field(min_length=1)
    configuration_digest: str = Field(min_length=1)
    parameters_digest: str = Field(min_length=1)
    code_revision: str = Field(min_length=1)
    environment: str = Field(min_length=1)
    executed_at: datetime
    prediction_origin: datetime | None = None
    forecast_horizon_seconds: int | None = Field(default=None, ge=0)
    output_digest: str = Field(min_length=1)
    benchmark_id: str | None = None
    validation_state: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_reproducibility(self) -> "ScientificExecutionRecord":
        if self.executed_at.tzinfo is None:
            raise ValueError("executed_at must be timezone-aware")
        if self.prediction_origin is not None:
            if self.prediction_origin.tzinfo is None:
                raise ValueError("prediction_origin must be timezone-aware")
            if self.prediction_origin > self.executed_at:
                raise ValueError("prediction_origin cannot be after executed_at")
        if self.execution_state == ScientificExecutionState.REPRODUCIBILITY_INCOMPLETE:
            raise ValueError("incomplete reproducibility cannot be recorded as a completed execution")
        if self.epistemic_boundary == ScientificBoundary.CAUSAL and self.validation_state == "UNVALIDATED":
            raise ValueError("unvalidated execution cannot claim a causal boundary")
        return self


class OutcomeAvailability(BaseModel):
    """Point-in-time outcome metadata; absence of an outcome is explicit."""

    model_config = ConfigDict(extra="forbid")

    outcome_id: str = Field(min_length=1)
    outcome_time: datetime
    available_at: datetime | None = None
    observed: bool = False
    vintage_id: str = Field(min_length=1)
    definition_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_time(self) -> "OutcomeAvailability":
        if self.outcome_time.tzinfo is None:
            raise ValueError("outcome_time must be timezone-aware")
        if self.available_at is not None:
            if self.available_at.tzinfo is None:
                raise ValueError("available_at must be timezone-aware")
            if self.available_at < self.outcome_time:
                raise ValueError("available_at cannot precede outcome_time")
        if self.observed and self.available_at is None:
            raise ValueError("observed outcomes require available_at")
        return self

    def eligible_at(self, cutoff: datetime) -> bool:
        if cutoff.tzinfo is None:
            raise ValueError("cutoff must be timezone-aware")
        return self.observed and self.available_at is not None and self.available_at <= cutoff


@dataclass(frozen=True)
class ReliabilityBin:
    lower: float
    upper: float
    count: int
    mean_probability: float | None
    observed_frequency: float | None


def canonical_digest(value: object) -> str:
    """Stable SHA-256 digest for JSON-compatible scientific metadata."""
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def require_point_in_time(
    availability_times: Sequence[datetime], prediction_origin: datetime
) -> None:
    """Fail closed if any input was unavailable at prediction origin."""
    if prediction_origin.tzinfo is None:
        raise ValueError("prediction_origin must be timezone-aware")
    for available_at in availability_times:
        if available_at.tzinfo is None:
            raise ValueError("all availability timestamps must be timezone-aware")
        if available_at > prediction_origin:
            raise ValueError("future information is not eligible at prediction origin")


def reliability_curve(
    probabilities: Sequence[float],
    outcomes: Sequence[int],
    *,
    bins: int = 10,
) -> tuple[ReliabilityBin, ...]:
    """Return deterministic equal-width reliability bins."""
    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must have equal length")
    if not probabilities:
        raise ValueError("at least one forecast is required")
    if bins < 2:
        raise ValueError("bins must be at least 2")
    if any(not 0 <= p <= 1 for p in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    if any(y not in (0, 1) for y in outcomes):
        raise ValueError("outcomes must be binary")

    groups: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for probability, outcome in zip(probabilities, outcomes):
        index = min(bins - 1, int(probability * bins))
        groups[index].append((probability, outcome))

    result: list[ReliabilityBin] = []
    for index, group in enumerate(groups):
        lower = index / bins
        upper = (index + 1) / bins
        if not group:
            result.append(ReliabilityBin(lower, upper, 0, None, None))
            continue
        result.append(
            ReliabilityBin(
                lower,
                upper,
                len(group),
                sum(p for p, _ in group) / len(group),
                sum(y for _, y in group) / len(group),
            )
        )
    return tuple(result)


def calibration_slope(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    """Estimate binary calibration slope by Newton iterations on logit(p).

    The function is intentionally a diagnostic, not a validation decision.
    Perfect separation or degenerate probabilities return a finite neutral
    diagnostic only when the data identify a slope; otherwise an explicit error
    is raised rather than inventing a value.
    """
    if len(probabilities) != len(outcomes) or not probabilities:
        raise ValueError("equal non-empty probability/outcome sequences are required")
    if any(not 0 < p < 1 for p in probabilities):
        raise ValueError("calibration slope requires probabilities strictly between 0 and 1")
    if any(y not in (0, 1) for y in outcomes):
        raise ValueError("outcomes must be binary")
    x = [math.log(p / (1 - p)) for p in probabilities]
    if len(set(x)) < 2 or all(y == outcomes[0] for y in outcomes):
        raise ValueError("calibration slope is not identifiable from the supplied outcomes")

    slope = 1.0
    for _ in range(50):
        eta = [slope * value for value in x]
        fitted = [1 / (1 + math.exp(-max(-700.0, min(700.0, value)))) for value in eta]
        gradient = sum(value * (y - p) for value, y, p in zip(x, outcomes, fitted))
        hessian = -sum(value * value * p * (1 - p) for value, p in zip(x, fitted))
        if abs(hessian) < 1e-12:
            raise ValueError("calibration slope is numerically unstable")
        update = gradient / hessian
        slope -= update
        if abs(update) < 1e-10:
            return slope
    raise ValueError("calibration slope did not converge")


def sharpness(probabilities: Sequence[float]) -> float:
    """Forecast concentration diagnostic: variance of predicted probabilities."""
    if not probabilities:
        raise ValueError("at least one probability is required")
    if any(not 0 <= p <= 1 for p in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    mean = sum(probabilities) / len(probabilities)
    return sum((p - mean) ** 2 for p in probabilities) / len(probabilities)


def mean_absolute_calibration_error(
    probabilities: Sequence[float], outcomes: Sequence[int], *, bins: int = 10
) -> float:
    """Weighted absolute reliability error across populated bins."""
    curve = reliability_curve(probabilities, outcomes, bins=bins)
    total = sum(item.count for item in curve)
    return sum(
        item.count * abs(item.mean_probability - item.observed_frequency)
        for item in curve
        if item.count and item.mean_probability is not None and item.observed_frequency is not None
    ) / total


def build_execution_record(
    *,
    execution_id: str,
    capability_id: str,
    epistemic_boundary: ScientificBoundary,
    input_ids: Sequence[str],
    source_ids: Sequence[str],
    model_version: str,
    data_vintage: str,
    configuration: Mapping[str, object],
    parameters: Mapping[str, object],
    code_revision: str,
    environment: str,
    executed_at: datetime,
    output: object,
    prediction_origin: datetime | None = None,
    forecast_horizon_seconds: int | None = None,
    benchmark_id: str | None = None,
    validation_state: str = "NOT_VALIDATED",
) -> ScientificExecutionRecord:
    """Construct a reproducible execution record from explicit metadata."""
    return ScientificExecutionRecord(
        execution_id=execution_id,
        capability_id=capability_id,
        execution_state=ScientificExecutionState.EXECUTED,
        epistemic_boundary=epistemic_boundary,
        input_ids=tuple(input_ids),
        source_ids=tuple(source_ids),
        model_version=model_version,
        data_vintage=data_vintage,
        configuration_digest=canonical_digest(configuration),
        parameters_digest=canonical_digest(parameters),
        code_revision=code_revision,
        environment=environment,
        executed_at=executed_at,
        prediction_origin=prediction_origin,
        forecast_horizon_seconds=forecast_horizon_seconds,
        output_digest=canonical_digest(output),
        benchmark_id=benchmark_id,
        validation_state=validation_state,
    )
