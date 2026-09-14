"""
CeutIA - Modelo Temporal Multitemporal (P0)

Se distinguen explícitamente todos los tiempos relevantes. La frontera
analítica canónica de disponibilidad sigue siendo ``revision_time`` cuando
existe, después ``publication_time`` y finalmente ``ingestion_time``; event_time
nunca determina disponibilidad.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TimeRole(str, Enum):
    EVENT = "event_time"
    PUBLICATION = "publication_time"
    INGESTION = "ingestion_time"
    REVISION = "revision_time"
    DETECTION = "detection_time"
    ASSESSMENT = "assessment_time"
    IMPACT = "impact_time"


def _require_aware(value: Optional[datetime], field: str) -> None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError(f"{field} must be timezone-aware")


@dataclass(frozen=True)
class TemporalContext:
    event_time: Optional[datetime] = None
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    publication_time: Optional[datetime] = None
    ingestion_time: Optional[datetime] = None
    revision_time: Optional[datetime] = None
    detection_time: Optional[datetime] = None
    assessment_time: Optional[datetime] = None
    impact_time: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None

    def __post_init__(self) -> None:
        # Legacy construction permits naive timestamps. Retrospective and
        # validity comparisons fail closed unless their query boundary and
        # compared timestamps are timezone-aware.
        if self.event_start is not None and self.event_end is not None and self.event_start > self.event_end:
            raise ValueError("event_start must not be after event_end")
        if self.valid_from is not None and self.valid_to is not None and self.valid_from >= self.valid_to:
            raise ValueError("valid_from must be earlier than valid_to")

    @property
    def available_at(self) -> Optional[datetime]:
        return self.revision_time or self.publication_time or self.ingestion_time

    def is_available_at(self, simulation_time: datetime) -> bool:
        _require_aware(simulation_time, "simulation_time")
        available = self.available_at
        _require_aware(available, "available_at")
        return available is not None and available <= simulation_time

    def is_valid_at(self, simulation_time: datetime) -> bool:
        _require_aware(simulation_time, "simulation_time")
        _require_aware(self.valid_from, "valid_from")
        _require_aware(self.valid_to, "valid_to")
        if self.valid_from is not None and simulation_time < self.valid_from:
            return False
        if self.valid_to is not None and simulation_time >= self.valid_to:
            return False
        return True

    def to_dict(self) -> dict:
        def ser(dt: Optional[datetime]):
            return dt.isoformat() if dt else None
        return {
            "event_time": ser(self.event_time),
            "event_start": ser(self.event_start),
            "event_end": ser(self.event_end),
            "publication_time": ser(self.publication_time),
            "available_at": ser(self.available_at),
            "ingestion_time": ser(self.ingestion_time),
            "revision_time": ser(self.revision_time),
            "detection_time": ser(self.detection_time),
            "assessment_time": ser(self.assessment_time),
            "impact_time": ser(self.impact_time),
            "valid_from": ser(self.valid_from),
            "valid_to": ser(self.valid_to),
        }


class TemporalFilter:
    @staticmethod
    def _available_at(evidence) -> Optional[datetime]:
        available = getattr(evidence, "available_at", None)
        if callable(available):
            available = available()
        if available is not None:
            return available
        if hasattr(evidence, "to_dict"):
            value = evidence.to_dict().get("available_at")
            if value:
                return datetime.fromisoformat(value)
        return None

    @staticmethod
    def _version(evidence) -> Optional[int]:
        """Return the canonical evidence revision number."""
        version = getattr(evidence, "version", None)
        if version is None:
            version = getattr(evidence, "revision", None)
        return version

    @classmethod
    def filter_by_available_at(cls, evidences: List, simulation_time: datetime) -> List:
        """Return only evidence available and effective at simulation_time."""
        _require_aware(simulation_time, "simulation_time")
        result = []
        for evidence in evidences:
            available = cls._available_at(evidence)
            _require_aware(available, "evidence.available_at")
            if available is None or available > simulation_time:
                continue
            is_valid = getattr(evidence, "is_valid_at", None)
            if callable(is_valid) and not is_valid(simulation_time):
                continue
            result.append(evidence)
        return result

    @classmethod
    def snapshot_by_available_at(cls, evidences: List, simulation_time: datetime) -> List:
        """Return the latest available immutable version of each evidence item."""
        available = cls.filter_by_available_at(evidences, simulation_time)
        selected: dict[object, object] = {}
        for evidence in available:
            evidence_id = getattr(evidence, "evidence_id", None)
            version = cls._version(evidence)
            if evidence_id is None or version is None or not isinstance(version, int) or version < 0:
                raise ValueError("point-in-time snapshot requires evidence_id and non-negative integer version")
            current = selected.get(evidence_id)
            if current is None:
                selected[evidence_id] = evidence
                continue
            current_version = cls._version(current)
            current_available = cls._available_at(current)
            available_now = cls._available_at(evidence)
            if (version, available_now) > (current_version, current_available):
                selected[evidence_id] = evidence
        return [evidence for evidence in evidences if selected.get(getattr(evidence, "evidence_id", object())) is evidence]

    @classmethod
    def filter_by_ingestion_time(cls, evidences: List, simulation_time: datetime, time_attr: str = "ingestion_time") -> List:
        """Compatibility alias; canonical analytical filtering uses available_at."""
        return cls.filter_by_available_at(evidences, simulation_time)

    @classmethod
    def assert_no_future_leak(cls, evidences: List, simulation_time: datetime) -> None:
        _require_aware(simulation_time, "simulation_time")
        leaks = []
        for ev in evidences:
            available = cls._available_at(ev)
            _require_aware(available, "evidence.available_at")
            if available is not None and available > simulation_time:
                eid = getattr(ev, "evidence_id", "unknown")
                leaks.append(f"{eid} (available_at={available.isoformat()})")
        if leaks:
            raise ValueError(
                f"Contaminación retrospectiva detectada en backtest (T={simulation_time.isoformat()}): "
                + ", ".join(leaks)
            )
