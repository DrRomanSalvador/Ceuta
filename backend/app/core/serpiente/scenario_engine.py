from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    probability: float
    assumptions: tuple[str, ...]
    cascade_nodes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be in [0,1]")


class ScenarioEngine:
    def normalize(self, scenarios: tuple[Scenario, ...]) -> tuple[Scenario, ...]:
        total = sum(s.probability for s in scenarios)
        if total <= 0.0:
            raise ValueError("scenario probabilities must have positive mass")
        return tuple(Scenario(s.scenario_id, s.probability / total, s.assumptions, s.cascade_nodes) for s in scenarios)
