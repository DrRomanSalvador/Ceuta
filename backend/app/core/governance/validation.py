from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationResult:
    component: str
    passed: bool
    metrics: tuple[tuple[str, float], ...]
    evidence_ids: tuple[str, ...]


class ProspectiveValidationHarness:
    def validate(self, component: str, *, predictions: tuple[float, ...], outcomes: tuple[float, ...], evidence_ids: tuple[str, ...]) -> ValidationResult:
        if len(predictions) != len(outcomes) or not predictions:
            raise ValueError("predictions and outcomes must have equal non-zero length")
        mae = sum(abs(a - b) for a, b in zip(predictions, outcomes)) / len(predictions)
        return ValidationResult(component, True, (("mae", mae),), evidence_ids)


class CrossDomainConsistency:
    def check(self, values: tuple[float, ...], *, tolerance: float) -> bool:
        return bool(values) and max(values) - min(values) <= tolerance


class UncertaintyPropagation:
    def combine(self, standard_deviations: tuple[float, ...]) -> float:
        if any(v < 0 for v in standard_deviations):
            raise ValueError("standard deviations must be non-negative")
        return sum(v * v for v in standard_deviations) ** 0.5


class ModelDisagreement:
    def score(self, predictions: tuple[float, ...]) -> float:
        if not predictions:
            raise ValueError("predictions must not be empty")
        mean = sum(predictions) / len(predictions)
        return sum(abs(v - mean) for v in predictions) / len(predictions)
