from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from math import isfinite
from typing import Final, Mapping, Protocol
from uuid import UUID, uuid4


class CitizenSignalValidationError(ValueError):
    """Raised when a citizen signal violates an epistemic or temporal contract."""


class TemporalLeakageError(CitizenSignalValidationError):
    """Raised when an event becomes available before it occurred."""


class ProvenanceError(CitizenSignalValidationError):
    """Raised when provenance is absent or malformed."""


class AnonymizationError(CitizenSignalValidationError):
    """Raised when a signal contains prohibited direct identifiers."""


class EventPublisher(Protocol):
    async def publish(self, event_type: str, event: object) -> None:
        ...


@dataclass(frozen=True, slots=True)
class SignalProvenance:
    source_type: str
    source_reference: str
    content_hash: str
    extraction_method: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.source_type.strip():
            raise ProvenanceError("source_type cannot be empty")
        if not self.source_reference.strip():
            raise ProvenanceError("source_reference cannot be empty")
        if len(self.content_hash) != 64:
            raise ProvenanceError("content_hash must be a SHA-256 hexadecimal digest")
        if any(character not in "0123456789abcdef" for character in self.content_hash):
            raise ProvenanceError("content_hash must contain lowercase hexadecimal characters")
        if not self.extraction_method.strip():
            raise ProvenanceError("extraction_method cannot be empty")
        _require_aware_datetime(self.created_at)


@dataclass(frozen=True, slots=True)
class StructuredUserSignal:
    signal_id: UUID
    session_id_hash: str
    event_time: datetime
    available_at: datetime
    domain: str
    signal_type: str
    description: str
    value: float | None
    unit: str | None
    confidence: float
    anonymized: bool
    provenance: SignalProvenance
    correlation_id: UUID

    def __post_init__(self) -> None:
        _require_aware_datetime(self.event_time)
        _require_aware_datetime(self.available_at)

        if self.available_at < self.event_time:
            raise TemporalLeakageError(
                "available_at cannot precede event_time"
            )

        if len(self.session_id_hash) != 64:
            raise AnonymizationError(
                "session_id_hash must be a SHA-256 digest"
            )

        if not self.domain.strip():
            raise CitizenSignalValidationError("domain cannot be empty")

        if not self.signal_type.strip():
            raise CitizenSignalValidationError("signal_type cannot be empty")

        if not self.description.strip():
            raise CitizenSignalValidationError("description cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise CitizenSignalValidationError(
                "confidence must be within [0, 1]"
            )

        if self.value is not None and not isfinite(self.value):
            raise CitizenSignalValidationError(
                "signal value must be finite"
            )

        if not self.anonymized:
            raise AnonymizationError(
                "citizen signals must be anonymized before publication"
            )


@dataclass(frozen=True, slots=True)
class CitizenInteraction:
    session_id: str
    event_time: datetime
    available_at: datetime
    domain: str
    signal_type: str
    description: str
    value: float | None
    unit: str | None
    confidence: float
    source_reference: str
    extraction_method: str


class CitizenSignalBridge:
    EVENT_TYPE: Final[str] = "citizen.signal.structured"

    def __init__(self, event_bus: EventPublisher) -> None:
        self._event_bus = event_bus

    async def process(
        self,
        interaction: CitizenInteraction,
    ) -> StructuredUserSignal:
        self._validate_interaction(interaction)

        session_hash = _hash_identifier(interaction.session_id)

        canonical_payload = "|".join(
            (
                session_hash,
                interaction.event_time.isoformat(),
                interaction.available_at.isoformat(),
                interaction.domain,
                interaction.signal_type,
                interaction.description,
                "" if interaction.value is None else repr(interaction.value),
                "" if interaction.unit is None else interaction.unit,
                repr(interaction.confidence),
            )
        )

        provenance = SignalProvenance(
            source_type="citizen_conversation",
            source_reference=interaction.source_reference,
            content_hash=sha256(
                canonical_payload.encode("utf-8")
            ).hexdigest(),
            extraction_method=interaction.extraction_method,
            created_at=datetime.now(timezone.utc),
        )

        signal = StructuredUserSignal(
            signal_id=uuid4(),
            session_id_hash=session_hash,
            event_time=interaction.event_time,
            available_at=interaction.available_at,
            domain=interaction.domain,
            signal_type=interaction.signal_type,
            description=interaction.description,
            value=interaction.value,
            unit=interaction.unit,
            confidence=interaction.confidence,
            anonymized=True,
            provenance=provenance,
            correlation_id=uuid4(),
        )

        await self._event_bus.publish(self.EVENT_TYPE, signal)
        return signal

    @staticmethod
    def _validate_interaction(interaction: CitizenInteraction) -> None:
        _require_aware_datetime(interaction.event_time)
        _require_aware_datetime(interaction.available_at)

        if interaction.available_at < interaction.event_time:
            raise TemporalLeakageError(
                "available_at cannot precede event_time"
            )

        if not interaction.session_id.strip():
            raise AnonymizationError("session_id cannot be empty")

        if not interaction.domain.strip():
            raise CitizenSignalValidationError("domain cannot be empty")

        if not interaction.signal_type.strip():
            raise CitizenSignalValidationError(
                "signal_type cannot be empty"
            )

        if not interaction.description.strip():
            raise CitizenSignalValidationError(
                "description cannot be empty"
            )

        if not interaction.source_reference.strip():
            raise ProvenanceError("source_reference cannot be empty")

        if not interaction.extraction_method.strip():
            raise ProvenanceError("extraction_method cannot be empty")

        if not 0.0 <= interaction.confidence <= 1.0:
            raise CitizenSignalValidationError(
                "confidence must be within [0, 1]"
            )

        if interaction.value is not None and not isfinite(interaction.value):
            raise CitizenSignalValidationError(
                "value must be finite"
            )


def _hash_identifier(value: str) -> str:
    normalized = value.strip().encode("utf-8")
    if not normalized:
        raise AnonymizationError("cannot hash an empty identifier")
    return sha256(normalized).hexdigest()


def _require_aware_datetime(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CitizenSignalValidationError(
            "timestamps must be timezone-aware"
        )