from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tradeoff:
    option_id: str
    benefit: float
    harm: float
    resource_cost: float
    score: float


class TradeoffEngine:
    def rank(self, options: tuple[tuple[str, float, float, float], ...]) -> tuple[Tradeoff, ...]:
        result = [Tradeoff(i, b, h, c, b - h - c) for i, b, h, c in options]
        return tuple(sorted(result, key=lambda x: (-x.score, x.option_id)))
