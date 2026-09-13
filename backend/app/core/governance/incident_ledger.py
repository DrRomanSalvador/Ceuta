from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Incident:
    incident_id: str
    severity: str
    occurred_at: datetime
    component: str
    description: str
    resolved: bool = False


class IncidentLedger:
    def __init__(self) -> None:
        self._items: list[Incident] = []

    def record(self, incident: Incident) -> None:
        if incident.occurred_at.tzinfo is None or incident.occurred_at.utcoffset() is None:
            raise ValueError("incident timestamp must be timezone-aware")
        self._items.append(incident)

    @property
    def incidents(self) -> tuple[Incident, ...]:
        return tuple(self._items)
