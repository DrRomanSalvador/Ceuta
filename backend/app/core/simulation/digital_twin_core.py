from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class SimulationState:
    values: tuple[float, ...]
    step: int


class DigitalTwinCore:
    def run(self, initial: SimulationState, transition: Callable[[SimulationState], SimulationState], *, steps: int) -> tuple[SimulationState, ...]:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        states = [initial]
        current = initial
        for _ in range(steps):
            next_state = transition(current)
            if next_state.step <= current.step:
                raise ValueError("simulation transition must advance step")
            states.append(next_state)
            current = next_state
        return tuple(states)
