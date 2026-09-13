"""Missingness, censoring and observation-process primitives.

Missingness is represented as part of the data-generating/observation process.
The module does not infer MCAR/MAR/MNAR from labels alone; callers must provide
the evidence supporting the classification.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MissingnessMechanism(StrEnum):
    OBSERVED = "observed"
    MCAR = "MCAR"
    MAR = "MAR"
    MNAR = "MNAR"
    CENSORED = "censored"
    TRUNCATED = "truncated"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MissingObservation:
    variable: str
    entity_id: str
    expected_window: tuple[str, str]
    mechanism: MissingnessMechanism
    reason: str | None = None
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.variable or not self.entity_id:
            raise ValueError("variable and entity_id are required")
        if len(self.expected_window) != 2:
            raise ValueError("expected_window requires start and end")
        if self.mechanism in {MissingnessMechanism.MCAR, MissingnessMechanism.MAR, MissingnessMechanism.MNAR} and not self.evidence_ids:
            raise ValueError("classified missingness requires evidence_ids")


@dataclass(frozen=True, slots=True)
class ObservationProcessChange:
    process_id: str
    effective_at: str
    previous_process: str
    new_process: str
    affected_variables: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.process_id, self.effective_at, self.previous_process, self.new_process)):
            raise ValueError("observation-process change metadata is incomplete")
        if not self.affected_variables or not self.evidence_ids:
            raise ValueError("process changes require affected variables and evidence")


class MissingnessAnalyzer:
    @staticmethod
    def expected_but_not_observed(expected_count: int, observed_count: int) -> bool:
        if expected_count < 0 or observed_count < 0 or observed_count > expected_count:
            raise ValueError("invalid expected/observed counts")
        return observed_count < expected_count

    @staticmethod
    def rate(expected_count: int, observed_count: int) -> float:
        if expected_count <= 0 or observed_count < 0 or observed_count > expected_count:
            raise ValueError("invalid expected/observed counts")
        return (expected_count - observed_count) / expected_count
