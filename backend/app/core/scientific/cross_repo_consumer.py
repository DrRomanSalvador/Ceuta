"""CeutIA-side consumer for the canonical SERPIENTE scientific contract."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import sqlite3
from typing import Any

from .cross_repo_contract import ScientificPredictionMessage, validate_scientific_prediction_payload
from .transport_security import verify_and_consume_transport


@dataclass(frozen=True, slots=True)
class CrossRepoAcceptance:
    accepted: bool
    reason: str
    prediction: ScientificPredictionMessage | None


def _transport_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = payload.get("_transport")
    if not isinstance(envelope, dict):
        raise ValueError("transport_missing:authenticated producer transport is required")
    required = {"timestamp", "nonce", "signature"}
    if set(envelope) != required:
        raise ValueError("transport_invalid:timestamp, nonce and signature are required")
    scientific_payload = {key: value for key, value in payload.items() if key != "_transport"}
    return scientific_payload, envelope


def consume_serpiente_prediction(payload: dict[str, Any], *, decision_time: datetime | None = None) -> CrossRepoAcceptance:
    """Authenticate, replay-protect and scientifically evaluate a SERPIENTE prediction."""
    try:
        scientific_payload, transport = _transport_payload(payload)
        secret = os.getenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "").strip()
        database_path = os.getenv("CEUTIA_DECISION_DB", "").strip()
        if not secret or not database_path:
            raise ValueError("transport_not_configured:producer transport secret and decision database are required")
        connection = sqlite3.connect(database_path, timeout=10.0)
        try:
            verify_and_consume_transport(connection, scientific_payload, secret=secret, timestamp=str(transport["timestamp"]), nonce=str(transport["nonce"]), signature=str(transport["signature"]), now=decision_time)
        finally:
            connection.close()
        prediction = validate_scientific_prediction_payload(scientific_payload)
    except (TypeError, ValueError, KeyError) as exc:
        return CrossRepoAcceptance(False, str(exc), None)
    if decision_time is not None:
        if decision_time.tzinfo is None or decision_time.utcoffset() is None:
            return CrossRepoAcceptance(False, "temporally_ineligible:decision_time_not_timezone_aware", prediction)
        reference_time = decision_time.astimezone(timezone.utc)
        if prediction.origin_time.astimezone(timezone.utc) > reference_time:
            return CrossRepoAcceptance(False, "temporally_ineligible:prediction_origin_in_future", prediction)
        if prediction.available_at.astimezone(timezone.utc) > reference_time:
            return CrossRepoAcceptance(False, "temporally_ineligible:prediction_not_available", prediction)
    if prediction.ood_state == "OUT_OF_DISTRIBUTION":
        return CrossRepoAcceptance(False, "scientifically_incompatible:out_of_distribution", prediction)
    if prediction.ood_state == "UNKNOWN":
        return CrossRepoAcceptance(False, "scientifically_incompatible:ood_unknown", prediction)
    if prediction.calibration_status != "CALIBRATED":
        return CrossRepoAcceptance(False, "scientifically_incompatible:uncalibrated", prediction)
    if prediction.source_independence == "UNKNOWN":
        return CrossRepoAcceptance(False, "scientifically_incompatible:source_dependence_unknown", prediction)
    return CrossRepoAcceptance(True, "scientifically_compatible", prediction)


__all__ = ["CrossRepoAcceptance", "consume_serpiente_prediction"]
