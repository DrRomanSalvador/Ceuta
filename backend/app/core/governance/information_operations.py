from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InformationOperationAssessment:
    operation_id: str
    amplification: float
    coordination: float
    targeting: float
    alert: bool


class InformationOperationDetector:
    def assess(self, operation_id: str, *, amplification: float, coordination: float, targeting: float, threshold: float = 0.7) -> InformationOperationAssessment:
        score = (amplification + coordination + targeting) / 3.0
        return InformationOperationAssessment(operation_id, amplification, coordination, targeting, score >= threshold)
