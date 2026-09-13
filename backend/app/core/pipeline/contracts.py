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


def _require_nonempty_sequence(values: tuple[str, ...], field_name: str) -> None:
    if not values or any(not value for value in values):
        raise ValueError(f"{field_name} must contain at least one non-empty value")


@dataclass(frozen=True, slots=True)
class PipelineEvent:
    """Envelope used by the asynchronous event bus."""

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
        for name in ("observation_id", "variable", "domain", "provenance_hash"):
            if not getattr(self, name):
                raise ValueError(f"{name} must not be empty")
        if not isfinite(float(self.value)):
            raise ValueError("value must be finite")
        _require_aware(self.event_time, "event_time")
        _require_aware(self.available_at, "available_at")
        if self.available_at < self.event_time:
            raise ValueError("available_at cannot precede event_time")
        _require_nonempty_sequence(self.source_ids, "source_ids")
        if any(not value for value in self.evidence_ids):
            raise ValueError("evidence_ids must not contain empty values")
        if not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class VariableState:
    """Current dynamic state of one observed variable."""

    variable: str
    value: float
    previous_value: float | None
    velocity: float | None
    acceleration: float | None
    observations: int
    updated_at: datetime
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.variable:
            raise ValueError("variable must not be empty")
        for name in ("value", "previous_value", "velocity", "acceleration"):
            value = getattr(self, name)
            if value is not None and not isfinite(float(value)):
                raise ValueError(f"{name} must be finite when provided")
        if self.observations < 1:
            raise ValueError("observations must be positive")
        _require_aware(self.updated_at, "updated_at")
        if any(not value for value in self.evidence_ids):
            raise ValueError("evidence_ids must not contain empty values")


@dataclass(frozen=True, slots=True)
class DomainState:
    """Immutable aggregate state for one system domain."""

    domain: str
    variables: tuple[VariableState, ...]
    observation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.domain:
            raise ValueError("domain must not be empty")
        if any(not isinstance(item, VariableState) for item in self.variables):
            raise TypeError("variables must contain only VariableState objects")
        _require_nonempty_sequence(self.observation_ids, "observation_ids")
        if len({item.variable for item in self.variables}) != len(self.variables):
            raise ValueError("domain variables must be unique")


@dataclass(frozen=True, slots=True)
class Interaction:
    """Observed association between two variables; not a causal assertion."""

    upstream: str
    downstream: str
    coupling: float
    lag_steps: int = 1
    mechanism: str = "association"

    def __post_init__(self) -> None:
        if not self.upstream or not self.downstream:
            raise ValueError("interaction endpoints are required")
        if self.upstream == self.downstream:
            raise ValueError("self-interactions are not supported")
        if not isfinite(float(self.coupling)) or not 0.0 <= self.coupling <= 1.0:
            raise ValueError("coupling must be finite and between 0 and 1")
        if self.lag_steps < 1:
            raise ValueError("lag_steps must be >= 1")
        if not self.mechanism:
            raise ValueError("mechanism must not be empty")


@dataclass(frozen=True, slots=True)
class InteractionEffect:
    """Computed dynamic association effect; explicitly non-causal."""

    upstream: str
    downstream: str
    coupling: float
    upstream_velocity: float
    estimated_effect: float
    interpretation: str = "association-based dynamic coupling; not causal"
    status: str = "UNVERIFIED"

    def __post_init__(self) -> None:
        if not self.upstream or not self.downstream:
            raise ValueError("interaction endpoints are required")
        for name in ("coupling", "upstream_velocity", "estimated_effect"):
            if not isfinite(float(getattr(self, name))):
                raise ValueError(f"{name} must be finite")
        if not 0.0 <= self.coupling <= 1.0:
            raise ValueError("coupling must be between 0 and 1")
        if not self.interpretation or not self.status:
            raise ValueError("interpretation and status must not be empty")


@dataclass(frozen=True, slots=True)
class SystemStateContract:
    """Auditable multidomain system state emitted by the state stage."""

    state_id: str
    as_of: datetime
    domains: tuple[DomainState, ...]
    interactions: tuple[Interaction, ...]
    interaction_effects: tuple[InteractionEffect, ...]
    observation_ids: tuple[str, ...]
    schema_version: str

    def __post_init__(self) -> None:
        if not self.state_id or not self.schema_version:
            raise ValueError("state_id and schema_version must not be empty")
        _require_aware(self.as_of, "as_of")
        if not self.domains:
            raise ValueError("system state must contain at least one domain")
        if any(not isinstance(item, DomainState) for item in self.domains):
            raise TypeError("domains must contain only DomainState objects")
        if len({item.domain for item in self.domains}) != len(self.domains):
            raise ValueError("system state domains must be unique")
        _require_nonempty_sequence(self.observation_ids, "observation_ids")
        if any(not isinstance(item, Interaction) for item in self.interactions):
            raise TypeError("interactions must contain only Interaction objects")
        if any(not isinstance(item, InteractionEffect) for item in self.interaction_effects):
            raise TypeError("interaction_effects must contain only InteractionEffect objects")
        for domain in self.domains:
            for variable in domain.variables:
                if variable.updated_at > self.as_of:
                    raise ValueError("variable state cannot be newer than system as_of")
