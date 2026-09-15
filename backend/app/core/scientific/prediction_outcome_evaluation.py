"""Durable prospective prediction -> observed outcome evaluation."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import sqlite3
from typing import Any


SCHEMA_VERSION = 1


def ensure_prediction_outcome_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS scientific_prediction_outcomes (
            prediction_id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            outcome_id TEXT NOT NULL UNIQUE,
            target TEXT NOT NULL,
            outcome_time TEXT NOT NULL,
            observed INTEGER NOT NULL CHECK(observed IN (0,1)),
            predicted_probability REAL NOT NULL,
            brier_error REAL NOT NULL,
            log_loss_error REAL NOT NULL,
            provenance_json TEXT NOT NULL,
            recorded_at TEXT NOT NULL
        )"""
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_prediction_outcomes_decision "
        "ON scientific_prediction_outcomes(decision_id, outcome_time)"
    )
    connection.commit()


def _log_loss(probability: float, observed: int) -> float:
    bounded = min(max(probability, 1e-8), 1.0 - 1e-8)
    return float(-(observed * math.log(bounded) + (1 - observed) * math.log(1.0 - bounded)))


def record_prediction_outcome(
    connection: sqlite3.Connection,
    *,
    prediction_id: str,
    decision_id: str,
    outcome_id: str,
    target: str,
    outcome_time: datetime,
    observed: int,
    provenance: tuple[str, ...],
) -> dict[str, Any]:
    """Link one persisted prediction to its point-in-time observed binary outcome."""
    if not prediction_id or not decision_id or not outcome_id or not target or not provenance:
        raise ValueError("prediction outcome identity and provenance are required")
    if outcome_time.tzinfo is None or outcome_time.utcoffset() is None:
        raise ValueError("outcome_time must be timezone-aware")
    if observed not in (0, 1):
        raise ValueError("observed outcome must be 0 or 1")

    ensure_prediction_outcome_schema(connection)
    prediction = connection.execute(
        "SELECT decision_id, available_at, payload_json FROM scientific_predictions WHERE prediction_id=?",
        (prediction_id,),
    ).fetchone()
    if prediction is None:
        raise KeyError("prediction_id not found")
    stored_decision_id, available_at_raw, payload_raw = prediction
    if stored_decision_id != decision_id:
        raise ValueError("prediction does not belong to decision_id")
    payload = json.loads(payload_raw)
    if str(payload["target"]) != target:
        raise ValueError("outcome target does not match prediction target")
    available_at = datetime.fromisoformat(str(available_at_raw))
    if available_at.tzinfo is None or available_at.utcoffset() is None:
        raise RuntimeError("persisted prediction availability timestamp is not timezone-aware")
    normalized_outcome_time = outcome_time.astimezone(timezone.utc)
    if normalized_outcome_time < available_at.astimezone(timezone.utc):
        raise ValueError("outcome cannot precede prediction availability")

    probability = float(payload["probability"])
    brier_error = float((probability - observed) ** 2)
    log_loss_error = _log_loss(probability, observed)
    canonical_provenance = tuple(dict.fromkeys(str(item) for item in provenance))
    row = connection.execute(
        "SELECT decision_id, outcome_id, target, outcome_time, observed, predicted_probability, brier_error, log_loss_error, provenance_json "
        "FROM scientific_prediction_outcomes WHERE prediction_id=?",
        (prediction_id,),
    ).fetchone()
    values = (
        decision_id,
        outcome_id,
        target,
        normalized_outcome_time.isoformat(),
        observed,
        probability,
        brier_error,
        log_loss_error,
        json.dumps(canonical_provenance, sort_keys=True, separators=(",", ":")),
    )
    if row is not None:
        if row != values:
            raise RuntimeError("prediction outcome identity collision: existing outcome differs")
        return {
            "prediction_id": prediction_id,
            "decision_id": decision_id,
            "outcome_id": outcome_id,
            "target": target,
            "observed": observed,
            "predicted_probability": probability,
            "brier_error": brier_error,
            "log_loss_error": log_loss_error,
            "outcome_time": normalized_outcome_time.isoformat(),
            "provenance": canonical_provenance,
        }

    existing_outcome = connection.execute(
        "SELECT prediction_id FROM scientific_prediction_outcomes WHERE outcome_id=?",
        (outcome_id,),
    ).fetchone()
    if existing_outcome is not None and existing_outcome[0] != prediction_id:
        raise RuntimeError("outcome identity collision: outcome_id is already linked to another prediction")
    recorded_at = datetime.now(timezone.utc).isoformat()
    connection.execute(
        "INSERT INTO scientific_prediction_outcomes(prediction_id,decision_id,outcome_id,target,outcome_time,observed,predicted_probability,brier_error,log_loss_error,provenance_json,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (prediction_id, *values, recorded_at),
    )
    connection.commit()
    return {
        "prediction_id": prediction_id,
        "decision_id": decision_id,
        "outcome_id": outcome_id,
        "target": target,
        "observed": observed,
        "predicted_probability": probability,
        "brier_error": brier_error,
        "log_loss_error": log_loss_error,
        "outcome_time": normalized_outcome_time.isoformat(),
        "provenance": canonical_provenance,
    }


def get_prediction_outcome(connection: sqlite3.Connection, prediction_id: str) -> dict[str, Any] | None:
    ensure_prediction_outcome_schema(connection)
    row = connection.execute(
        "SELECT prediction_id, decision_id, outcome_id, target, outcome_time, observed, predicted_probability, brier_error, log_loss_error, provenance_json, recorded_at FROM scientific_prediction_outcomes WHERE prediction_id=?",
        (prediction_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "prediction_id": row[0],
        "decision_id": row[1],
        "outcome_id": row[2],
        "target": row[3],
        "outcome_time": row[4],
        "observed": row[5],
        "predicted_probability": row[6],
        "brier_error": row[7],
        "log_loss_error": row[8],
        "provenance": tuple(json.loads(row[9])),
        "recorded_at": row[10],
    }


__all__ = ["SCHEMA_VERSION", "ensure_prediction_outcome_schema", "get_prediction_outcome", "record_prediction_outcome"]
