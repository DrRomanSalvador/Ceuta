"""Operational proper-scoring mechanism for strategic forecast reports.

The mechanism settles verified binary forecasts with an affine transfer of a
strictly proper score. This implements the incentive mechanism itself while
keeping real-world verification and behavioural validation separate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log
import sqlite3


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
    strict-propriety guarantee. ``storage_path`` enables durable settlement
    state without coupling this mechanism to the primary decision database.
    """

    def __init__(self, *, stake: float = 1.0, storage_path: str | None = None) -> None:
        if not isfinite(stake) or stake <= 0:
            raise ValueError("stake must be finite and positive")
        self.stake = stake
        self._reports: dict[str, ForecastReport] = {}
        self._settlements: dict[str, Settlement] = {}
        self._storage_path = storage_path
        if storage_path is not None:
            self._init_storage()
            self._load_storage()

    def _connect(self) -> sqlite3.Connection:
        if self._storage_path is None:
            raise RuntimeError("persistent storage is not configured")
        return sqlite3.connect(self._storage_path)

    def _init_storage(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS forecast_reports (
                    report_id TEXT PRIMARY KEY,
                    forecaster_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    probability REAL NOT NULL,
                    submitted_at TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    outcome_due_at TEXT NOT NULL,
                    UNIQUE(forecaster_id, question_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS forecast_settlements (
                    report_id TEXT PRIMARY KEY REFERENCES forecast_reports(report_id),
                    outcome INTEGER NOT NULL,
                    log_loss REAL NOT NULL,
                    transfer REAL NOT NULL,
                    verified_at TEXT NOT NULL,
                    verifier_id TEXT NOT NULL
                )"""
            )

    def _load_storage(self) -> None:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT report_id, forecaster_id, question_id, probability, submitted_at, deadline, outcome_due_at FROM forecast_reports"
            ).fetchall()
            for row in rows:
                self._reports[row[0]] = ForecastReport(
                    row[0], row[1], row[2], row[3],
                    datetime.fromisoformat(row[4]), datetime.fromisoformat(row[5]), datetime.fromisoformat(row[6])
                )
            rows = connection.execute(
                "SELECT report_id, outcome, log_loss, transfer, verified_at, verifier_id FROM forecast_settlements"
            ).fetchall()
            for row in rows:
                self._settlements[row[0]] = Settlement(
                    row[0], row[1], row[2], row[3], datetime.fromisoformat(row[4]), row[5]
                )

    def submit(self, report: ForecastReport) -> None:
        if report.report_id in self._reports:
            raise ValueError("duplicate report_id")
        if any(
            existing.forecaster_id == report.forecaster_id
            and existing.question_id == report.question_id
            for existing in self._reports.values()
        ):
            raise ValueError("one report per forecaster and question is required")
        if self._storage_path is not None:
            with self._connect() as connection:
                connection.execute(
                    "INSERT INTO forecast_reports VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (report.report_id, report.forecaster_id, report.question_id, report.probability,
                     report.submitted_at.isoformat(), report.deadline.isoformat(), report.outcome_due_at.isoformat()),
                )
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
        if self._storage_path is not None:
            with self._connect() as connection:
                connection.execute(
                    "INSERT INTO forecast_settlements VALUES (?, ?, ?, ?, ?, ?)",
                    (settlement.report_id, settlement.outcome, settlement.log_loss,
                     settlement.transfer, settlement.verified_at.isoformat(), settlement.verifier_id),
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
        if belief not in candidate_reports:
            return False
        truthful = cls.expected_log_loss(belief, belief)
        alternatives = tuple(
            cls.expected_log_loss(p, belief) for p in candidate_reports if p != belief
        )
        return not alternatives or truthful < min(alternatives) - tolerance


__all__ = ["ForecastReport", "ProperScoringMechanism", "Settlement"]
