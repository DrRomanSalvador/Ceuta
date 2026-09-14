"""Intervention-independent validation and outcome contamination ledger.

A warning that changes the outcome cannot be scored as an ordinary false
positive unless a defensible counterfactual is supplied. Prediction accuracy
and prevention effectiveness are therefore persisted as distinct quantities.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
import sqlite3


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


class ValidationLane(StrEnum):
    SHADOW = "shadow"
    CONTROL = "control"
    INTERVENTION = "intervention"


class EvaluationStatus(StrEnum):
    SCOREABLE = "scoreable"
    NOT_SCOREABLE = "not_scoreable"
    COUNTERFACTUAL_REQUIRED = "counterfactual_required"


@dataclass(frozen=True, slots=True)
class ValidationObservation:
    observation_id: str
    prediction_id: str
    lane: ValidationLane
    warning_issued: bool
    intervention_applied: bool
    event_occurred: bool | None
    counterfactual_event_probability: float | None
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    created_at: str

    def __post_init__(self) -> None:
        if not self.observation_id or not self.prediction_id:
            raise ValueError("observation and prediction identity are required")
        if not self.evidence_refs or not self.provenance_refs:
            raise ValueError("validation observation requires provenance")
        if self.counterfactual_event_probability is not None and not 0 <= self.counterfactual_event_probability <= 1:
            raise ValueError("counterfactual probability must be in [0,1]")

    @property
    def evaluation_status(self) -> EvaluationStatus:
        if self.intervention_applied and self.counterfactual_event_probability is None:
            return EvaluationStatus.COUNTERFACTUAL_REQUIRED
        if self.event_occurred is None:
            return EvaluationStatus.NOT_SCOREABLE
        return EvaluationStatus.SCOREABLE

    @property
    def ordinary_accuracy_label(self) -> str | None:
        if self.evaluation_status is not EvaluationStatus.SCOREABLE:
            return None
        if self.warning_issued and self.event_occurred:
            return "true_positive"
        if not self.warning_issued and not self.event_occurred:
            return "true_negative"
        if self.warning_issued and not self.event_occurred:
            return "false_positive"
        return "false_negative"


class InterventionIndependentValidationLedger:
    """Durable, integrity-checked validation lanes."""

    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS intervention_validation(
                observation_id TEXT PRIMARY KEY,
                prediction_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                record_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")

    def append(self, observation: ValidationObservation) -> None:
        payload = _canonical({
            "observation_id": observation.observation_id,
            "prediction_id": observation.prediction_id,
            "lane": observation.lane.value,
            "warning_issued": observation.warning_issued,
            "intervention_applied": observation.intervention_applied,
            "event_occurred": observation.event_occurred,
            "counterfactual_event_probability": observation.counterfactual_event_probability,
            "evidence_refs": observation.evidence_refs,
            "provenance_refs": observation.provenance_refs,
            "created_at": observation.created_at,
        })
        digest = sha256(payload.encode()).hexdigest()
        with sqlite3.connect(self.storage_path) as db:
            if db.execute("SELECT 1 FROM intervention_validation WHERE observation_id=?", (observation.observation_id,)).fetchone():
                raise ValueError("validation observation already exists")
            db.execute("INSERT INTO intervention_validation VALUES(?,?,?,?,?)", (
                observation.observation_id, observation.prediction_id, payload, digest, observation.created_at,
            ))

    def verify_integrity(self) -> bool:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT observation_id,payload,record_hash FROM intervention_validation ORDER BY created_at,observation_id").fetchall()
        return all(sha256(payload.encode()).hexdigest() == record_hash for _, payload, record_hash in rows)


__all__ = [
    "EvaluationStatus", "InterventionIndependentValidationLedger",
    "ValidationLane", "ValidationObservation",
]
