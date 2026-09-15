"""Product-level scientific prediction replay and outcome endpoints."""
from __future__ import annotations

import hmac
import os
import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .cross_repo_contract import validate_scientific_prediction_payload
from .prediction_outcome_evaluation import record_prediction_outcome
from .prediction_persistence import replay_prediction


router = APIRouter(prefix="/scientific", tags=["scientific"])
DECISION_KEY_HEADER = "X-CeutIA-Decision-Key"


class PredictionOutcomeRequest(BaseModel):
    prediction_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    outcome_id: str = Field(min_length=1)
    target: str = Field(min_length=1)
    outcome_time: datetime
    observed: int = Field(ge=0, le=1)
    provenance: list[str] = Field(min_length=1)


def _authorize(request: Request) -> JSONResponse | None:
    configured_key = os.getenv("CEUTIA_DECISION_API_KEY", "").strip()
    provided_key = request.headers.get(DECISION_KEY_HEADER, "")
    if not configured_key:
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": "CEUTIA_DECISION_API_KEY is not configured"})
    if not provided_key or not hmac.compare_digest(provided_key, configured_key):
        return JSONResponse(status_code=401, content={"error": "unauthorized"})
    return None


def _database_path() -> str:
    path = os.getenv("CEUTIA_DECISION_DB", "").strip()
    if not path:
        raise RuntimeError("CEUTIA_DECISION_DB is not configured")
    return path


@router.get("/predictions/{prediction_id}/replay")
async def replay_scientific_prediction(prediction_id: str, request: Request, as_of: datetime):
    denied = _authorize(request)
    if denied is not None:
        return denied
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        return JSONResponse(status_code=422, content={"error": "replay as_of must be timezone-aware"})
    try:
        connection = sqlite3.connect(_database_path(), timeout=10.0)
        try:
            payload = replay_prediction(connection, prediction_id, as_of=as_of)
            prediction = validate_scientific_prediction_payload(payload)
        finally:
            connection.close()
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except (RuntimeError, ValueError) as exc:
        return JSONResponse(status_code=422, content={"error": str(exc)})
    return {
        "prediction_id": prediction.prediction_id,
        "as_of": as_of.astimezone(timezone.utc).isoformat(),
        "point_in_time_eligible": True,
        "scientific_contract_valid": True,
        "prediction": payload,
    }


@router.post("/predictions/outcomes")
async def record_scientific_prediction_outcome(request: Request, payload: PredictionOutcomeRequest):
    denied = _authorize(request)
    if denied is not None:
        return denied
    if payload.outcome_time.tzinfo is None or payload.outcome_time.utcoffset() is None:
        return JSONResponse(status_code=422, content={"error": "outcome_time must be timezone-aware"})
    try:
        connection = sqlite3.connect(_database_path(), timeout=10.0)
        try:
            result = record_prediction_outcome(
                connection,
                prediction_id=payload.prediction_id,
                decision_id=payload.decision_id,
                action_id=payload.action_id,
                outcome_id=payload.outcome_id,
                target=payload.target,
                outcome_time=payload.outcome_time,
                observed=payload.observed,
                provenance=tuple(payload.provenance),
            )
        finally:
            connection.close()
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except (RuntimeError, ValueError) as exc:
        return JSONResponse(status_code=422, content={"error": str(exc)})
    return result


__all__ = ["PredictionOutcomeRequest", "router"]
