from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class Agent:
    agent_id: str
    state: float


class AgentStressTester:
    def run(self, agents: tuple[Agent, ...], policy: Callable[[Agent], Agent], *, rounds: int) -> tuple[Agent, ...]:
        if rounds < 0:
            raise ValueError("rounds must be non-negative")
        current = agents
        for _ in range(rounds):
            current = tuple(policy(agent) for agent in current)
        return current
