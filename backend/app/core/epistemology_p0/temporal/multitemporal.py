"""
CeutIA - Modelo Temporal Multitemporal (P0)

No se utiliza un único campo timestamp.
Se distinguen explícitamente todos los tiempos relevantes.
Crítico para backtesting sin contaminación retrospectiva.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
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

    def is_available_at(self, simulation_time: datetime) -> bool:
        if self.ingestion_time is None:
            return False
        return self.ingestion_time <= simulation_time

    def to_dict(self) -> dict:
        def ser(dt: Optional[datetime]):
            return dt.isoformat() if dt else None
        return {
            "event_time": ser(self.event_time),
            "event_start": ser(self.event_start),
            "event_end": ser(self.event_end),
            "publication_time": ser(self.publication_time),
            "ingestion_time": ser(self.ingestion_time),
            "revision_time": ser(self.revision_time),
            "detection_time": ser(self.detection_time),
            "assessment_time": ser(self.assessment_time),
            "impact_time": ser(self.impact_time),
        }


class TemporalFilter:
    @staticmethod
    def filter_by_ingestion_time(evidences: List, simulation_time: datetime, time_attr: str = "ingestion_time") -> List:
        result = []
        for ev in evidences:
            ing = getattr(ev, time_attr, None)
            if ing is None and hasattr(ev, "to_dict"):
                d = ev.to_dict()
                ing_str = d.get("ingestion_time")
                if ing_str:
                    ing = datetime.fromisoformat(ing_str)
            if ing is not None and ing <= simulation_time:
                result.append(ev)
        return result

    @staticmethod
    def assert_no_future_leak(evidences: List, simulation_time: datetime) -> None:
        leaks = []
        for ev in evidences:
            ing = getattr(ev, "ingestion_time", None)
            if ing and ing > simulation_time:
                eid = getattr(ev, "evidence_id", "unknown")
                leaks.append(f"{eid} (ingestion={ing.isoformat()})")
        if leaks:
            raise ValueError(
                f"Contaminación retrospectiva detectada en backtest (T={simulation_time.isoformat()}): "
                + ", ".join(leaks)
            )
