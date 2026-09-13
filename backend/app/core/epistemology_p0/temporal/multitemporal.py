"""
CeutIA - Modelo Temporal Multitemporal (P0)

Se distinguen explícitamente todos los tiempos relevantes. La única frontera
analítica es ``available_at``: event_time nunca determina disponibilidad.
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

    @property
    def available_at(self) -> Optional[datetime]:
        return self.revision_time or self.publication_time or self.ingestion_time

    def is_available_at(self, simulation_time: datetime) -> bool:
        available = self.available_at
        return available is not None and available <= simulation_time

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

    @classmethod
    def filter_by_available_at(cls, evidences: List, simulation_time: datetime) -> List:
        """Return only evidence known to be available at simulation_time."""
        return [
            ev for ev in evidences
            if (available := cls._available_at(ev)) is not None
            and available <= simulation_time
        ]

    @classmethod
    def filter_by_ingestion_time(cls, evidences: List, simulation_time: datetime, time_attr: str = "ingestion_time") -> List:
        """Compatibility alias; the requested attribute is intentionally ignored.

        Historical callers cannot select an alternative temporal gate. All
        analytical filtering is performed through the canonical available_at
        boundary.
        """
        return cls.filter_by_available_at(evidences, simulation_time)

    @classmethod
    def assert_no_future_leak(cls, evidences: List, simulation_time: datetime) -> None:
        leaks = []
        for ev in evidences:
            available = cls._available_at(ev)
            if available is not None and available > simulation_time:
                eid = getattr(ev, "evidence_id", "unknown")
                leaks.append(f"{eid} (available_at={available.isoformat()})")
        if leaks:
            raise ValueError(
                f"Contaminación retrospectiva detectada en backtest (T={simulation_time.isoformat()}): "
                + ", ".join(leaks)
            )
