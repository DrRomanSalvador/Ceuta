"""Outcome accounting for reflexive early-warning systems.

A warning followed by successful intervention cannot be naively labelled a
false positive: the observed non-event is compatible with prevention. This
ledger therefore separates observed outcomes from counterfactual claims and
forbids ordinary accuracy scoring when the counterfactual state is not
identified.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import json
import sqlite3
from hashlib import sha256


class InterventionOutcomeStatus(StrEnum):
    EVENT_OCCURRED = "event_occurred"
    EVENT_AVERTED = "event_averted"
    NO_EVENT_NO_INTERVENTION = "no_event_no_intervention"
    OUTCOME_UNCERTAIN = "outcome_uncertain"


@dataclass(frozen=True, slots=True)
class InterventionOutcome:
    warning_id: str
    intervention_id: str
    status: InterventionOutcomeStatus
    outcome_reference: str
    counterfactual_identified: bool
    observed_at: datetime

    def __post_init__(self) -> None:
        if not self.warning_id or not self.intervention_id or not self.outcome_reference:
            raise ValueError("warning, intervention and outcome references are required")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.status == InterventionOutcomeStatus.EVENT_AVERTED and not self.counterfactual_identified:
            raise ValueError("event_averted requires an identified counterfactual")

    @property
    def ordinary_accuracy_label(self) -> str:
        if self.status == InterventionOutcomeStatus.EVENT_OCCURRED:
            return "true_positive"
        if self.status == InterventionOutcomeStatus.NO_EVENT_NO_INTERVENTION:
            return "true_negative"
        return "not_scoreable_as_ordinary_accuracy"


class InterventionOutcomeLedger:
    """Durable, fail-closed settlement ledger for reflexive warnings."""

    VERSION = "intervention-outcomes-v1"

    def __init__(self, *, storage_path: str | None = None) -> None:
        self.storage_path = storage_path
        self._outcomes: dict[str, InterventionOutcome] = {}
        if storage_path:
            self._init_db(); self._load_db()

    def _db(self) -> sqlite3.Connection:
        if not self.storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self.storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS intervention_outcomes(warning_id TEXT PRIMARY KEY, payload TEXT NOT NULL, record_hash TEXT NOT NULL)")

    def _load_db(self) -> None:
        with self._db() as db:
            for warning_id, payload, record_hash in db.execute("SELECT warning_id,payload,record_hash FROM intervention_outcomes"):
                if sha256(payload.encode()).hexdigest() != record_hash:
                    raise ValueError("intervention outcome integrity failure")
                p = json.loads(payload)
                self._outcomes[warning_id] = InterventionOutcome(warning_id, p["intervention_id"], InterventionOutcomeStatus(p["status"]), p["outcome_reference"], p["counterfactual_identified"], datetime.fromisoformat(p["observed_at"]))

    def settle(self, outcome: InterventionOutcome) -> None:
        if outcome.warning_id in self._outcomes:
            raise ValueError("duplicate warning outcome")
        self._outcomes[outcome.warning_id] = outcome
        if self.storage_path:
            payload = json.dumps({"intervention_id": outcome.intervention_id, "status": outcome.status.value, "outcome_reference": outcome.outcome_reference, "counterfactual_identified": outcome.counterfactual_identified, "observed_at": outcome.observed_at.isoformat()}, sort_keys=True, separators=(",", ":"))
            with self._db() as db:
                db.execute("INSERT INTO intervention_outcomes VALUES(?,?,?)", (outcome.warning_id, payload, sha256(payload.encode()).hexdigest()))

    def scoreable_counts(self) -> dict[str, int]:
        counts = {"true_positive": 0, "true_negative": 0, "not_scoreable_as_ordinary_accuracy": 0}
        for outcome in self._outcomes.values():
            counts[outcome.ordinary_accuracy_label] += 1
        return counts

    def outcomes(self) -> tuple[InterventionOutcome, ...]:
        return tuple(self._outcomes.values())


__all__ = ["InterventionOutcomeStatus", "InterventionOutcome", "InterventionOutcomeLedger"]
