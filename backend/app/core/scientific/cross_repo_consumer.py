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
    if set(envelope) != {"timestamp", "nonce", "signature"}:
        raise ValueError("transport_invalid:timestamp, nonce and signature are required")
    return {key: value for key, value in payload.items() if key != "_transport"}, envelope


def consume_serpiente_prediction(payload: dict[str, Any], *, decision_time: datetime | None = None) -> CrossRepoAcceptance:
    """Authenticate and enforce scientific eligibility before a prediction can enter decision persistence."""
    try:
        transport_present = "_transport" in payload
        secret = os.getenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "").strip()
        database_path = os.getenv("CEUTIA_DECISION_DB", "").strip()
        if transport_present:
            scientific_payload, transport = _transport_payload(payload)
            if not secret or not database_path:
                raise ValueError("transport_not_configured:producer transport secret and decision database are required")
            connection = sqlite3.connect(database_path, timeout=10.0)
            try:
                verify_and_consume_transport(connection, scientific_payload, secret=secret, timestamp=str(transport["timestamp"]), nonce=str(transport["nonce"]), signature=str(transport["signature"]), now=decision_time)
            finally:
                connection.close()
        elif secret:
            raise ValueError("transport_missing:authenticated producer transport is required")
        else:
            scientific_payload = payload
        prediction = validate_scientific_prediction_payload(scientific_payload)
    except (TypeError, ValueError, KeyError) as exc:
        return CrossRepoAcceptance(False, str(exc), None)
    if decision_time is not None:
        if decision_time.tzinfo is None or decision_time.utcoffset() is None:
            return CrossRepoAcceptance(False, "temporally_ineligible:decision_time_not_timezone_aware", None)
        reference_time = decision_time.astimezone(timezone.utc)
        if prediction.origin_time.astimezone(timezone.utc) > reference_time:
            return CrossRepoAcceptance(False, "temporally_ineligible:prediction_origin_in_future", None)
        if prediction.available_at.astimezone(timezone.utc) > reference_time:
            return CrossRepoAcceptance(False, "temporally_ineligible:prediction_not_available", None)
    if prediction.ood_state == "OUT_OF_DISTRIBUTION":
        return CrossRepoAcceptance(False, "scientifically_incompatible:out_of_distribution", None)
    if prediction.ood_state == "UNKNOWN":
        return CrossRepoAcceptance(False, "scientifically_incompatible:ood_unknown", None)
    if prediction.calibration_status != "CALIBRATED":
        return CrossRepoAcceptance(False, "scientifically_incompatible:uncalibrated", None)
    if prediction.source_independence == "UNKNOWN":
        return CrossRepoAcceptance(False, "scientifically_incompatible:source_dependence_unknown", None)
    return CrossRepoAcceptance(True, "scientifically_compatible", prediction)


__all__ = ["CrossRepoAcceptance", "consume_serpiente_prediction"]
