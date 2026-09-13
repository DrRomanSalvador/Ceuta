from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProspectiveOutcome:
    forecast_id: str
    prediction: float
    outcome: float
    error: float


class ProspectiveLearningLoop:
    def record(self, forecast_id: str, *, prediction: float, outcome: float) -> ProspectiveOutcome:
        return ProspectiveOutcome(forecast_id, prediction, outcome, outcome - prediction)

    def mean_absolute_error(self, outcomes: tuple[ProspectiveOutcome, ...]) -> float:
        if not outcomes:
            raise ValueError("outcomes must not be empty")
        return sum(abs(o.error) for o in outcomes) / len(outcomes)
