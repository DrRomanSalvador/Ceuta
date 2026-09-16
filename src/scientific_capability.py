"""Executable scientific capability primitives for CeutIA/SERPIENTE.

These objects operationalize scientific gates without claiming scientific
validation. They enforce temporal eligibility, observation/denominator
semantics, identifiability state, baseline comparisons, probabilistic
forecast metrics, observation-process transformations, and decision utility
on explicit inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from math import erf, exp, log, pi, sqrt
from typing import Iterable, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EpistemicIdentifiability(StrEnum):
    IDENTIFIED = "IDENTIFIED"
    PARTIALLY_IDENTIFIED = "PARTIALLY_IDENTIFIED"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"


class ScientificCapabilityState(StrEnum):
    DOCUMENTED_ONLY = "DOCUMENTED_ONLY"
    FORMALIZED = "FORMALIZED"
    REPRESENTED = "REPRESENTED"
    IMPLEMENTED = "IMPLEMENTED"
    UNIT_TESTED = "UNIT_TESTED"
    INTEGRATION_TESTED = "INTEGRATION_TESTED"
    BENCHMARKED = "BENCHMARKED"
    RUNTIME_VERIFIED = "RUNTIME_VERIFIED"
    SCIENTIFICALLY_VALIDATED = "SCIENTIFICALLY_VALIDATED"
    PROSPECTIVELY_VALIDATED = "PROSPECTIVELY_VALIDATED"
    OPERATIONALLY_VALIDATED = "OPERATIONALLY_VALIDATED"
    ESTABLISHED = "ESTABLISHED"


class ObservationRecord(BaseModel):
    """A versioned observation with point-in-time semantics."""

    model_config = ConfigDict(extra="forbid")

    observation_id: str = Field(min_length=1)
    phenomenon_id: str = Field(min_length=1)
    value: float
    event_time: datetime
    observed_at: datetime
    publication_time: datetime | None = None
    revision_time: datetime | None = None
    knowledge_time: datetime
    vintage_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_temporal_semantics(self) -> "ObservationRecord":
        timestamps = {
            "event_time": self.event_time,
            "observed_at": self.observed_at,
            "publication_time": self.publication_time,
            "revision_time": self.revision_time,
            "knowledge_time": self.knowledge_time,
        }
        for name, value in timestamps.items():
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.knowledge_time < self.observed_at:
            raise ValueError("knowledge_time cannot precede observed_at")
        if self.publication_time is not None and self.knowledge_time < self.publication_time:
            raise ValueError("knowledge_time cannot precede publication_time")
        if self.revision_time is not None and self.knowledge_time < self.revision_time:
            raise ValueError("knowledge_time cannot precede revision_time")
        return self

    def eligible_at(self, prediction_origin: datetime) -> bool:
        if prediction_origin.tzinfo is None:
            raise ValueError("prediction_origin must be timezone-aware")
        return self.knowledge_time <= prediction_origin


class DynamicDenominator(BaseModel):
    """Denominator tied to population, exposure, coverage and time."""

    model_config = ConfigDict(extra="forbid")

    denominator_id: str = Field(min_length=1)
    population_definition: str = Field(min_length=1)
    population_at_risk: float = Field(gt=0)
    exposed_population: float | None = Field(default=None, gt=0)
    observed_population: float | None = Field(default=None, gt=0)
    period_start: datetime
    period_end: datetime
    geography: str = Field(min_length=1)
    coverage_fraction: float | None = Field(default=None, ge=0.0, le=1.0)
    definition_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_period(self) -> "DynamicDenominator":
        if self.period_start.tzinfo is None or self.period_end.tzinfo is None:
            raise ValueError("denominator period timestamps must be timezone-aware")
        if self.period_end <= self.period_start:
            raise ValueError("period_end must be after period_start")
        return self

    def rate(self, events: float) -> float:
        if events < 0:
            raise ValueError("events cannot be negative")
        return events / self.population_at_risk


class ObservationProcess(BaseModel):
    """Explicit observation mechanism; it is metadata, not a causal claim."""

    model_config = ConfigDict(extra="forbid")

    process_id: str = Field(min_length=1)
    phenomenon_id: str = Field(min_length=1)
    detection_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    reporting_fraction: float | None = Field(default=None, ge=0.0, le=1.0)
    coverage_fraction: float | None = Field(default=None, ge=0.0, le=1.0)
    delay_days: float | None = Field(default=None, ge=0.0)
    change_reason: str | None = None
    known_administrative_change: bool = False

    def observation_probability(self) -> float | None:
        factors = (
            self.detection_probability,
            self.reporting_fraction,
            self.coverage_fraction,
        )
        if any(value is None for value in factors):
            return None
        result = 1.0
        for value in factors:
            result *= value  # type: ignore[operator]
        return result

    def expected_observed_events(self, latent_events: float) -> float:
        if latent_events < 0:
            raise ValueError("latent_events cannot be negative")
        probability = self.observation_probability()
        if probability is None:
            raise ValueError("observation probability is not identified")
        return latent_events * probability

    def infer_latent_events(self, observed_events: float) -> float | None:
        """Invert the observation process only when its detection probability is known."""
        if observed_events < 0:
            raise ValueError("observed_events cannot be negative")
        probability = self.observation_probability()
        if probability is None or probability <= 0:
            return None
        return observed_events / probability


class IdentifiabilityAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity_id: str = Field(min_length=1)
    status: EpistemicIdentifiability
    informed_by: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    observationally_equivalent_alternatives: tuple[str, ...] = ()
    uncertainty_description: str = Field(min_length=1)
    resolving_data: tuple[str, ...] = ()

    @model_validator(mode="after")
    def require_alternatives_for_nonidentification(self) -> "IdentifiabilityAssessment":
        if (
            self.status == EpistemicIdentifiability.NOT_IDENTIFIABLE
            and not self.observationally_equivalent_alternatives
        ):
            raise ValueError(
                "NOT_IDENTIFIABLE requires at least one observationally equivalent alternative"
            )
        return self


@dataclass(frozen=True)
class BaselineScore:
    name: str
    brier: float | None = None
    log_score: float | None = None
    crps: float | None = None
    lead_time: float | None = None


@dataclass(frozen=True)
class IncrementalValue:
    delta_brier: float | None
    delta_log_score: float | None
    delta_crps: float | None
    delta_lead_time: float | None

    @property
    def has_any_improvement(self) -> bool:
        improvements = []
        if self.delta_brier is not None:
            improvements.append(self.delta_brier < 0)
        if self.delta_log_score is not None:
            improvements.append(self.delta_log_score > 0)
        if self.delta_crps is not None:
            improvements.append(self.delta_crps < 0)
        if self.delta_lead_time is not None:
            improvements.append(self.delta_lead_time > 0)
        return any(improvements)


@dataclass(frozen=True)
class ProbabilisticForecast:
    """Forecast distribution for one outcome and horizon."""

    mean: float
    std: float
    observed: float
    probability_positive: float | None = None

    def __post_init__(self) -> None:
        if self.std <= 0:
            raise ValueError("std must be positive")
        if self.probability_positive is not None and not 0 <= self.probability_positive <= 1:
            raise ValueError("probability_positive must be in [0, 1]")


@dataclass(frozen=True)
class DecisionOutcome:
    """Recorded decision/outcome pair for utility evaluation."""

    action_id: str
    predicted_probability: float
    outcome: int
    intervention_cost: float = 0.0
    false_positive_cost: float = 0.0
    false_negative_cost: float = 0.0
    delay_cost: float = 0.0

    def __post_init__(self) -> None:
        if not 0 <= self.predicted_probability <= 1:
            raise ValueError("predicted_probability must be in [0, 1]")
        if self.outcome not in (0, 1):
            raise ValueError("outcome must be binary")
        if min(
            self.intervention_cost,
            self.false_positive_cost,
            self.false_negative_cost,
            self.delay_cost,
        ) < 0:
            raise ValueError("decision costs cannot be negative")

    def realized_loss(self, action_taken: bool) -> float:
        loss = self.intervention_cost if action_taken else 0.0
        if action_taken and self.outcome == 0:
            loss += self.false_positive_cost
        if not action_taken and self.outcome == 1:
            loss += self.false_negative_cost
        return loss + self.delay_cost


def expected_binary_loss(
    probability: float,
    *,
    action_cost: float,
    false_positive_cost: float,
    false_negative_cost: float,
    delay_cost: float = 0.0,
) -> tuple[float, float]:
    """Return expected loss for no-action and action; caller chooses the action."""
    if not 0 <= probability <= 1:
        raise ValueError("probability must be in [0, 1]")
    if min(action_cost, false_positive_cost, false_negative_cost, delay_cost) < 0:
        raise ValueError("costs cannot be negative")
    no_action = probability * false_negative_cost + delay_cost
    action = action_cost + (1 - probability) * false_positive_cost + delay_cost
    return no_action, action


def brier_score(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    _validate_equal_lengths(probabilities, outcomes)
    if not probabilities:
        raise ValueError("at least one forecast is required")
    if any(p < 0 or p > 1 for p in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    if any(y not in (0, 1) for y in outcomes):
        raise ValueError("binary outcomes must be 0 or 1")
    return sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)


def log_score(probabilities: Sequence[float], outcomes: Sequence[int], eps: float = 1e-15) -> float:
    _validate_equal_lengths(probabilities, outcomes)
    if not probabilities:
        raise ValueError("at least one forecast is required")
    if eps <= 0 or eps >= 0.5:
        raise ValueError("eps must be between 0 and 0.5")
    total = 0.0
    for p, y in zip(probabilities, outcomes):
        if y not in (0, 1) or not 0 <= p <= 1:
            raise ValueError("binary outcomes and probabilities are required")
        p = min(1 - eps, max(eps, p))
        total += y * log(p) + (1 - y) * log(1 - p)
    return total / len(outcomes)


def normal_crps(mean: float, std: float, observed: float) -> float:
    """Exact CRPS for a normal predictive distribution."""
    if std <= 0:
        raise ValueError("std must be positive")
    z = (observed - mean) / std
    phi = exp(-0.5 * z * z) / sqrt(2 * pi)
    Phi = 0.5 * (1.0 + erf(z / sqrt(2.0)))
    return std * (z * (2 * Phi - 1) + 2 * phi - 1 / sqrt(pi))


def mean_crps(forecasts: Iterable[ProbabilisticForecast]) -> float:
    items = list(forecasts)
    if not items:
        raise ValueError("at least one forecast is required")
    return sum(normal_crps(x.mean, x.std, x.observed) for x in items) / len(items)


def calibration_in_the_large(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    """Observed event rate minus mean forecast probability."""
    _validate_equal_lengths(probabilities, outcomes)
    if not probabilities:
        raise ValueError("at least one forecast is required")
    if any(not 0 <= p <= 1 for p in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    if any(y not in (0, 1) for y in outcomes):
        raise ValueError("binary outcomes must be 0 or 1")
    return sum(outcomes) / len(outcomes) - sum(probabilities) / len(probabilities)


def compare_baselines(baseline: BaselineScore, candidate: BaselineScore) -> IncrementalValue:
    """Compute directional incremental value; no model is declared superior."""
    return IncrementalValue(
        delta_brier=(candidate.brier - baseline.brier)
        if candidate.brier is not None and baseline.brier is not None
        else None,
        delta_log_score=(candidate.log_score - baseline.log_score)
        if candidate.log_score is not None and baseline.log_score is not None
        else None,
        delta_crps=(candidate.crps - baseline.crps)
        if candidate.crps is not None and baseline.crps is not None
        else None,
        delta_lead_time=(candidate.lead_time - baseline.lead_time)
        if candidate.lead_time is not None and baseline.lead_time is not None
        else None,
    )


def point_in_time_filter(
    observations: Iterable[ObservationRecord], prediction_origin: datetime
) -> list[ObservationRecord]:
    """Return only observations known at prediction origin, preserving vintage."""
    if prediction_origin.tzinfo is None:
        raise ValueError("prediction_origin must be timezone-aware")
    return [item for item in observations if item.eligible_at(prediction_origin)]


def _validate_equal_lengths(left: Sequence[object], right: Sequence[object]) -> None:
    if len(left) != len(right):
        raise ValueError("forecast and outcome sequences must have equal length")
