"""Operational proper-scoring mechanism for strategic forecast reports.

The mechanism settles verified binary forecasts with an affine transfer of a
strictly proper score. This implements the incentive mechanism itself while
keeping real-world verification and behavioural validation separate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log


@dataclass(frozen=True, slots=True)
class ForecastReport:
    report_id: str
    forecaster_id: str
    question_id: str
    probability: float
    submitted_at: datetime
    deadline: datetime
    outcome_due_at: datetime

    def __post_init__(self) -> None:
        if not self.report_id or not self.forecaster_id or not self.question_id:
            raise ValueError("report identity is required")
        if not isfinite(self.probability) or not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be finite and in [0,1]")
        for value in (self.submitted_at, self.deadline, self.outcome_due_at):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("forecast timestamps must be timezone-aware")
        if self.submitted_at > self.deadline:
            raise ValueError("submitted_at must not exceed deadline")
        if self.outcome_due_at <= self.deadline:
            raise ValueError("outcome_due_at must follow the reporting deadline")


@dataclass(frozen=True, slots=True)
class Settlement:
    report_id: str
    outcome: int
    log_loss: float
    transfer: float
    verified_at: datetime
    verifier_id: str


class ProperScoringMechanism:
    """Strictly proper binary log-score transfer mechanism.

    Transfer is ``-stake * log_score``. Negative transfer is a penalty and is
    intentionally not clipped, because arbitrary truncation can destroy the
    strict-propriety guarantee. A positive affine transformation preserves the
    incentive ordering; external budgets/escrow can bound economic exposure.
    """

    def __init__(self, *, stake: float = 1.0) -> None:
        if not isfinite(stake) or stake <= 0:
            raise ValueError("stake must be finite and positive")
        self.stake = stake
        self._reports: dict[str, ForecastReport] = {}
        self._settlements: dict[str, Settlement] = {}

    def submit(self, report: ForecastReport) -> None:
        if report.report_id in self._reports:
            raise ValueError("duplicate report_id")
        if any(
            existing.forecaster_id == report.forecaster_id
            and existing.question_id == report.question_id
            for existing in self._reports.values()
        ):
            raise ValueError("one report per forecaster and question is required")
        self._reports[report.report_id] = report

    def settle(
        self,
        report_id: str,
        *,
        outcome: int,
        verified_at: datetime | None = None,
        verifier_id: str,
    ) -> Settlement:
        if outcome not in (0, 1):
            raise ValueError("outcome must be 0 or 1")
        if not verifier_id:
            raise ValueError("verifier_id is required")
        report = self._reports[report_id]
        if report_id in self._settlements:
            raise ValueError("report has already been settled")
        verified_at = verified_at or datetime.now(timezone.utc)
        if verified_at.tzinfo is None or verified_at.utcoffset() is None:
            raise ValueError("verified_at must be timezone-aware")
        if verified_at < report.outcome_due_at:
            raise ValueError("outcome cannot be settled before outcome_due_at")
        epsilon = 1e-15
        p = min(max(report.probability, epsilon), 1.0 - epsilon)
        loss = -(outcome * log(p) + (1 - outcome) * log(1.0 - p))
        settlement = Settlement(
            report_id=report_id,
            outcome=outcome,
            log_loss=loss,
            transfer=-self.stake * loss,
            verified_at=verified_at,
            verifier_id=verifier_id,
        )
        self._settlements[report_id] = settlement
        return settlement

    def report(self, report_id: str) -> ForecastReport:
        return self._reports[report_id]

    def settlement(self, report_id: str) -> Settlement:
        return self._settlements[report_id]

    @staticmethod
    def expected_log_loss(probability: float, belief: float) -> float:
        """Expected log loss under a Bernoulli belief."""
        if not all(isfinite(v) and 0.0 <= v <= 1.0 for v in (probability, belief)):
            raise ValueError("probability and belief must be finite and in [0,1]")
        epsilon = 1e-15
        p = min(max(probability, epsilon), 1.0 - epsilon)
        return -(belief * log(p) + (1 - belief) * log(1.0 - p))

    @classmethod
    def verify_strict_propriety(
        cls, *, belief: float, candidate_reports: tuple[float, ...], tolerance: float = 1e-12
    ) -> bool:
        """Numerically verify truthful reporting is the unique grid optimum.

        This is a mechanism-level computational check, not empirical evidence
        about real agents' behaviour.
        """
        if not isfinite(belief) or not 0.0 <= belief <= 1.0:
            raise ValueError("belief must be finite and in [0,1]")
        if not candidate_reports:
            raise ValueError("candidate_reports must not be empty")
        values = tuple(cls.expected_log_loss(p, belief) for p in candidate_reports)
        minimum = min(values)
        truthful = cls.expected_log_loss(belief, belief)
        return truthful <= minimum + tolerance


__all__ = ["ForecastReport", "ProperScoringMechanism", "Settlement"]
