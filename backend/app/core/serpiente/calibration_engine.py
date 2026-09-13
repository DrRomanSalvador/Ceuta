from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CalibrationState:
    model_id: str
    bias: float
    observations: int


class CalibrationEngine:
    def update(self, state: CalibrationState, *, prediction: float, outcome: float) -> CalibrationState:
        n = state.observations + 1
        error = outcome - prediction
        return CalibrationState(state.model_id, state.bias + (error - state.bias) / n, n)

    @staticmethod
    def correct(state: CalibrationState, prediction: float) -> float:
        return prediction + state.bias
