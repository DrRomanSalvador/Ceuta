"""Evidence-preserving sensing contracts for longitudinal real-time monitoring.

The sensing boundary converts heterogeneous producers into typed observations without
performing inference. It preserves event time, availability time, source identity,
quality, units, uncertainty and provenance so downstream state estimation can reason
about the observation process instead of treating incoming values as ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite
from typing import Mapping, Sequence

from app.core.errors import ContractViolation, TemporalViolation


@dataclass(frozen=True, slots=True)
class SignalDescriptor:
    signal_id: str
    variable: str
    unit: str | None
    domain: str
    source_id: str
    sampling_period_seconds: float | None = None
    expected_range: tuple[float, float] | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all((self.signal_id, self.variable, self.domain, self.source_id)):
            raise ContractViolation("signal identity fields are required")
        if self.sampling_period_seconds is not None and self.sampling_period_seconds <= 0:
            raise ContractViolation("sampling period must be positive")
        if self.expected_range is not None:
            low, high = self.expected_range
            if not isfinite(low) or not isfinite(high) or low >= high:
                raise ContractViolation("expected range must be finite and ordered")


@dataclass(frozen=True, slots=True)
class RawSignal:
    signal_id: str
    event_time: datetime
    available_at: datetime
    value: float
    uncertainty: float | None = None
    sequence: int | None = None
    payload_hash: str = ""
    quality: float = 1.0

    def __post_init__(self) -> None:
        if not self.signal_id or not self.payload_hash:
            raise ContractViolation("signal_id and payload_hash are required")
        for field_name, value in (("event_time", self.event_time), ("available_at", self.available_at)):
            if value.tzinfo is None or value.utcoffset() is None:
                raise TemporalViolation(f"{field_name} must be timezone-aware")
        if self.available_at < self.event_time:
            raise TemporalViolation("available_at cannot precede event_time")
        if not isfinite(self.value):
            raise ContractViolation("signal value must be finite")
        if self.uncertainty is not None and (self.uncertainty < 0 or not isfinite(self.uncertainty)):
            raise ContractViolation("uncertainty must be finite and non-negative")
        if not 0 <= self.quality <= 1:
            raise ContractViolation("quality must be between 0 and 1")


class SensorRegistry:
    """Authoritative signal metadata registry; unknown signals are rejected."""

    def __init__(self, descriptors: Sequence[SignalDescriptor] = ()) -> None:
        self._signals = {item.signal_id: item for item in descriptors}
        if len(self._signals) != len(tuple(descriptors)):
            raise ContractViolation("signal IDs must be unique")

    def register(self, descriptor: SignalDescriptor) -> None:
        if descriptor.signal_id in self._signals:
            raise ContractViolation(f"signal already registered: {descriptor.signal_id}")
        self._signals[descriptor.signal_id] = descriptor

    def describe(self, signal_id: str) -> SignalDescriptor:
        try:
            return self._signals[signal_id]
        except KeyError as exc:
            raise ContractViolation(f"unknown signal: {signal_id}") from exc

    def validate(self, signal: RawSignal) -> SignalDescriptor:
        descriptor = self.describe(signal.signal_id)
        if descriptor.expected_range is not None:
            low, high = descriptor.expected_range
            if not low <= signal.value <= high:
                raise ContractViolation(f"signal value outside declared range: {signal.signal_id}")
        return descriptor
