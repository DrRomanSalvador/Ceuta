"""Durable prospective prediction -> decision -> intervention -> outcome evaluation."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import math
import re
import sqlite3
from typing import Any

SCHEMA_VERSION = 5
_ALLOWED_CENSORING = {"NONE", "RIGHT", "LEFT", "INTERVAL", "UNKNOWN"}
_ALLOWED_MISSINGNESS = {"OBSERVED", "MISSING", "PARTIAL", "UNKNOWN"}
_ALLOWED_SELECTION = {"NONE", "OBSERVABLE_ONLY", "SELECTED", "UNKNOWN"}


def ensure_prediction_outcome_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS scientific_prediction_outcomes (
        prediction_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, action_id TEXT NOT NULL,
        outcome_id TEXT NOT NULL UNIQUE, target TEXT NOT NULL, outcome_time TEXT NOT NULL,
        observed INTEGER NOT NULL CHECK(observed IN (0,1)), predicted_probability REAL NOT NULL,
        brier_error REAL NOT NULL, log_loss_error REAL NOT NULL, provenance_json TEXT NOT NULL,
        recorded_at TEXT NOT NULL, source_id TEXT NOT NULL, source_version TEXT NOT NULL,
        observation_time TEXT NOT NULL, availability_time TEXT NOT NULL, ascertainment_time TEXT NOT NULL,
        revision_id TEXT NOT NULL, measurement_process_id TEXT NOT NULL, outcome_definition_version TEXT NOT NULL,
        transformation_id TEXT NOT NULL, censoring_status TEXT NOT NULL, missingness_status TEXT NOT NULL,
        selection_status TEXT NOT NULL, intervention_exposure_id TEXT)""")
    columns = {row[1] for row in connection.execute("PRAGMA table_info(scientific_prediction_outcomes)")}
    migrations = {
        "source_id": "TEXT NOT NULL DEFAULT ''", "source_version": "TEXT NOT NULL DEFAULT ''",
        "observation_time": "TEXT NOT NULL DEFAULT ''", "availability_time": "TEXT NOT NULL DEFAULT ''",
        "ascertainment_time": "TEXT NOT NULL DEFAULT ''", "revision_id": "TEXT NOT NULL DEFAULT ''",
        "measurement_process_id": "TEXT NOT NULL DEFAULT ''", "outcome_definition_version": "TEXT NOT NULL DEFAULT ''",
        "transformation_id": "TEXT NOT NULL DEFAULT ''", "censoring_status": "TEXT NOT NULL DEFAULT 'UNKNOWN'",
        "missingness_status": "TEXT NOT NULL DEFAULT 'UNKNOWN'", "selection_status": "TEXT NOT NULL DEFAULT 'UNKNOWN'",
        "intervention_exposure_id": "TEXT",
    }
    for name, definition in migrations.items():
        if columns and name not in columns:
            connection.execute(f"ALTER TABLE scientific_prediction_outcomes ADD COLUMN {name} {definition}")
    if columns and "action_id" not in columns:
        connection.execute("ALTER TABLE scientific_prediction_outcomes ADD COLUMN action_id TEXT NOT NULL DEFAULT ''")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_prediction_outcomes_decision ON scientific_prediction_outcomes(decision_id, outcome_time)")
    connection.commit()


def _log_loss(probability: float, observed: int) -> float:
    bounded = min(max(probability, 1e-8), 1.0 - 1e-8)
    return float(-(observed * math.log(bounded) + (1 - observed) * math.log(1.0 - bounded)))


def _horizon_delta(horizon: str) -> timedelta:
    value = horizon.strip().upper()
    iso = re.fullmatch(r"P(?:(?P<days>\d+(?:\.\d+)?)D)?(?:T(?:(?P<hours>\d+(?:\.\d+)?)H)?(?:(?P<minutes>\d+(?:\.\d+)?)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?", value)
    if iso and any(iso.group(name) is not None for name in ("days", "hours", "minutes", "seconds")):
        return timedelta(days=float(iso.group("days") or 0), hours=float(iso.group("hours") or 0), minutes=float(iso.group("minutes") or 0), seconds=float(iso.group("seconds") or 0))
    compact = re.fullmatch(r"(?P<value>\d+(?:\.\d+)?)(?P<unit>[SMHD])", value)
    if compact:
        amount = float(compact.group("value"))
        return {"S": timedelta(seconds=amount), "M": timedelta(minutes=amount), "H": timedelta(hours=amount), "D": timedelta(days=amount)}[compact.group("unit")]
    raise ValueError(f"unsupported prediction horizon for outcome alignment: {horizon}")


def _prediction_fingerprint(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    from hashlib import sha256
    return sha256(canonical.encode("utf-8")).hexdigest()


def _parse_aware(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def record_prediction_outcome(connection: sqlite3.Connection, *, prediction_id: str, decision_id: str, action_id: str,
                              outcome_id: str, target: str, outcome_time: datetime, observed: int,
                              provenance: tuple[str, ...], source_id: str, source_version: str,
                              observation_time: datetime, availability_time: datetime, ascertainment_time: datetime,
                              revision_id: str, measurement_process_id: str, outcome_definition_version: str,
                              transformation_id: str, censoring_status: str = "NONE",
                              missingness_status: str = "OBSERVED", selection_status: str = "NONE",
                              intervention_exposure_id: str | None = None) -> dict[str, Any]:
    """Link one persisted prediction to a fully ascertained point-in-time observed binary outcome."""
    required = (prediction_id, decision_id, action_id, outcome_id, target, source_id, source_version,
                revision_id, measurement_process_id, outcome_definition_version, transformation_id)
    if any(not value for value in required) or not provenance:
        raise ValueError("prediction outcome identity, provenance and ascertainment identity are required")
    if observed not in (0, 1):
        raise ValueError("observed outcome must be 0 or 1")
    if censoring_status not in _ALLOWED_CENSORING or missingness_status not in _ALLOWED_MISSINGNESS or selection_status not in _ALLOWED_SELECTION:
        raise ValueError("unsupported outcome ascertainment status")
    outcome_time = _parse_aware(outcome_time, "outcome_time")
    observation_time = _parse_aware(observation_time, "observation_time")
    availability_time = _parse_aware(availability_time, "availability_time")
    ascertainment_time = _parse_aware(ascertainment_time, "ascertainment_time")
    if observation_time > availability_time or availability_time > ascertainment_time:
        raise ValueError("outcome observation, availability and ascertainment times must be ordered")
    if missingness_status != "OBSERVED":
        raise ValueError("non-observed outcomes are not eligible for binary scoring")

    ensure_prediction_outcome_schema(connection)
    connection.execute("BEGIN IMMEDIATE")
    try:
        prediction = connection.execute("SELECT decision_id, available_at, payload_json, payload_fingerprint FROM scientific_predictions WHERE prediction_id=?", (prediction_id,)).fetchone()
        if prediction is None:
            raise KeyError("prediction_id not found")
        stored_decision_id, available_at_raw, payload_raw, stored_fingerprint = prediction
        if stored_decision_id != decision_id:
            raise ValueError("prediction does not belong to decision_id")
        payload = json.loads(payload_raw)
        if _prediction_fingerprint(payload) != str(stored_fingerprint):
            raise RuntimeError("prediction persistence integrity mismatch")
        probability = float(payload["probability"])
        if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError("persisted prediction probability is outside [0,1]")
        if str(payload["target"]) != target:
            raise ValueError("outcome target does not match prediction target")
        available_at = _parse_aware(datetime.fromisoformat(str(available_at_raw)), "persisted prediction availability timestamp")
        origin_time = _parse_aware(datetime.fromisoformat(str(payload["origin_time"])), "persisted prediction origin timestamp")
        if outcome_time > datetime.now(timezone.utc):
            raise ValueError("outcome cannot be in the future")
        if outcome_time < available_at:
            raise ValueError("outcome cannot precede prediction availability")
        if outcome_time < origin_time + _horizon_delta(str(payload["horizon"])):
            raise ValueError("outcome precedes prediction target time; prospective outcome is not yet eligible")
        if availability_time < available_at:
            raise ValueError("outcome availability cannot precede prediction availability")
        if ascertainment_time < availability_time:
            raise ValueError("outcome ascertainment cannot precede outcome availability")

        brier_error = float((probability - observed) ** 2)
        log_loss_error = _log_loss(probability, observed)
        canonical_provenance = tuple(dict.fromkeys(str(item) for item in provenance))
        values = (decision_id, action_id, outcome_id, target, outcome_time.isoformat(), observed, probability,
                  brier_error, log_loss_error, json.dumps(canonical_provenance, sort_keys=True, separators=(",", ":")),
                  source_id, source_version, observation_time.isoformat(), availability_time.isoformat(),
                  ascertainment_time.isoformat(), revision_id, measurement_process_id, outcome_definition_version,
                  transformation_id, censoring_status, missingness_status, selection_status, intervention_exposure_id)
        row = connection.execute("SELECT decision_id, action_id, outcome_id, target, outcome_time, observed, predicted_probability, brier_error, log_loss_error, provenance_json, source_id, source_version, observation_time, availability_time, ascertainment_time, revision_id, measurement_process_id, outcome_definition_version, transformation_id, censoring_status, missingness_status, selection_status, intervention_exposure_id FROM scientific_prediction_outcomes WHERE prediction_id=?", (prediction_id,)).fetchone()
        if row is not None:
            if row != values:
                raise RuntimeError("prediction outcome identity collision: existing outcome differs")
            connection.commit()
            return get_prediction_outcome(connection, prediction_id) or {}
        existing_outcome = connection.execute("SELECT prediction_id FROM scientific_prediction_outcomes WHERE outcome_id=?", (outcome_id,)).fetchone()
        if existing_outcome is not None and existing_outcome[0] != prediction_id:
            raise RuntimeError("outcome identity collision: outcome_id is already linked to another prediction")
        recorded_at = datetime.now(timezone.utc).isoformat()
        connection.execute("INSERT INTO scientific_prediction_outcomes(prediction_id,decision_id,action_id,outcome_id,target,outcome_time,observed,predicted_probability,brier_error,log_loss_error,provenance_json,recorded_at,source_id,source_version,observation_time,availability_time,ascertainment_time,revision_id,measurement_process_id,outcome_definition_version,transformation_id,censoring_status,missingness_status,selection_status,intervention_exposure_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (prediction_id, *values, recorded_at))
        connection.commit()
        return get_prediction_outcome(connection, prediction_id) or {}
    except Exception:
        connection.rollback()
        raise


def get_prediction_outcome(connection: sqlite3.Connection, prediction_id: str) -> dict[str, Any] | None:
    ensure_prediction_outcome_schema(connection)
    row = connection.execute("SELECT prediction_id, decision_id, action_id, outcome_id, target, outcome_time, observed, predicted_probability, brier_error, log_loss_error, provenance_json, recorded_at, source_id, source_version, observation_time, availability_time, ascertainment_time, revision_id, measurement_process_id, outcome_definition_version, transformation_id, censoring_status, missingness_status, selection_status, intervention_exposure_id FROM scientific_prediction_outcomes WHERE prediction_id=?", (prediction_id,)).fetchone()
    if row is None:
        return None
    return {"prediction_id": row[0], "decision_id": row[1], "action_id": row[2], "outcome_id": row[3], "target": row[4], "outcome_time": row[5], "observed": row[6], "predicted_probability": row[7], "brier_error": row[8], "log_loss_error": row[9], "provenance": tuple(json.loads(row[10])), "recorded_at": row[11], "source_id": row[12], "source_version": row[13], "observation_time": row[14], "availability_time": row[15], "ascertainment_time": row[16], "revision_id": row[17], "measurement_process_id": row[18], "outcome_definition_version": row[19], "transformation_id": row[20], "censoring_status": row[21], "missingness_status": row[22], "selection_status": row[23], "intervention_exposure_id": row[24]}


__all__ = ["SCHEMA_VERSION", "ensure_prediction_outcome_schema", "get_prediction_outcome", "record_prediction_outcome"]
