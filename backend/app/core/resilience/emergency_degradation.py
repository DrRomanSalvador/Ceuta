from __future__ import annotations

from enum import StrEnum


class DegradationLevel(StrEnum):
    NORMAL = "NORMAL"
    READ_ONLY = "READ_ONLY"
    EVIDENCE_ONLY = "EVIDENCE_ONLY"
    SAFE_STOP = "SAFE_STOP"


class EmergencyDegradation:
    def __init__(self) -> None:
        self._level = DegradationLevel.NORMAL

    @property
    def level(self) -> DegradationLevel:
        return self._level

    def enter(self, level: DegradationLevel) -> None:
        if level == DegradationLevel.NORMAL:
            raise ValueError("use recover() to return to NORMAL")
        self._level = level

    def recover(self) -> None:
        self._level = DegradationLevel.NORMAL

    def permits_mutation(self) -> bool:
        return self._level == DegradationLevel.NORMAL
