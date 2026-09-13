"""
P1 — Propagación de incertidumbre.

Serpiente debe usar la incertidumbre declarada para ajustar pesos,
no tratar todas las observaciones como igualmente fiables.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional
import math


@dataclass(frozen=True)
class IntervalUncertainty:
    lower: float
    upper: float
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("lower must be <= upper")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")

    @property
    def width(self) -> float:
        return self.upper - self.lower

    @property
    def midpoint(self) -> float:
        return (self.lower + self.upper) / 2.0

    def to_dict(self) -> dict:
        return {
            "type": "interval",
            "lower": self.lower,
            "upper": self.upper,
            "confidence": self.confidence,
            "width": self.width,
        }


def propagate_interval(
    value: float,
    *,
    relative_error: float = 0.0,
    absolute_error: float = 0.0,
    confidence: float = 1.0,
) -> IntervalUncertainty:
    """Propaga error relativo y absoluto a un intervalo alrededor de value."""
    if relative_error < 0 or absolute_error < 0:
        raise ValueError("errors must be non-negative")
    half = abs(value) * relative_error + absolute_error
    return IntervalUncertainty(
        lower=value - half,
        upper=value + half,
        confidence=confidence,
    )


def combine_uncertainties(
    intervals: Iterable[IntervalUncertainty],
    *,
    method: str = "max_width",
) -> Optional[IntervalUncertainty]:
    """Combina intervalos (conservador por defecto: max width / envelope)."""
    items = list(intervals)
    if not items:
        return None
    if method == "max_width":
        widest = max(items, key=lambda i: i.width)
        return widest
    if method == "envelope":
        return IntervalUncertainty(
            lower=min(i.lower for i in items),
            upper=max(i.upper for i in items),
            confidence=min(i.confidence for i in items),
        )
    if method == "rss":
        # Root-sum-square of half-widths around midpoints (independencia asumida)
        mid = sum(i.midpoint for i in items) / len(items)
        half = math.sqrt(sum((i.width / 2.0) ** 2 for i in items))
        conf = min(i.confidence for i in items)
        return IntervalUncertainty(lower=mid - half, upper=mid + half, confidence=conf)
    raise ValueError(f"unknown method: {method}")


def weight_by_confidence(confidence: float, dependence_ratio: float) -> float:
    """
    Peso efectivo para un modelo aguas abajo (p.ej. Serpiente).
    Penaliza baja confianza y alta dependencia entre fuentes.
    """
    c = max(0.0, min(1.0, confidence))
    d = max(0.0, min(1.0, dependence_ratio))
    return round(c * (1.0 - 0.7 * d), 6)
