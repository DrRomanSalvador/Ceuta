"""CeutIA canonical FastAPI application entrypoint."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.control_plane import EvidenceAssessment, EvidenceDisposition
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.information_boundary import InformationVisibility
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.decision.review_policy import DecisionRisk
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence, DecisionLifecycleEngine
from app.core.runtime.evidence_persistence import DecisionEvidenceStore
from app.core.runtime.integrity import validate_evidence_set, validate_scenario_probabilities
from app.core.runtime.model_governance import ModelGovernanceRecord

APP_NAME = "CeutIA"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Evidence-based territorial intelligence, knowledge and early-warning platform for Ceuta."
STATUS_RUNNING = "running"
STATUS_HEALTHY = "healthy"
STATUS_NOT_READY = "not_ready"
STATUS_READY = "ready"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
MIN_PORT = 1
MAX_PORT = 65535
LOGGER = logging.getLogger(APP_NAME)


def _configure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


_configure_logging()


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    host: str
    port: int
    code_revision: str
    decision_db: str


def _read_host() -> str:
    host = os.getenv("CEUTIA_HOST", DEFAULT_HOST).strip()
    if not host:
        raise ValueError("CEUTIA_HOST cannot be empty")
    return host


def _read_port() -> int:
    raw_port = os.getenv("CEUTIA_PORT", str(DEFAULT_PORT)).strip()
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("CEUTIA_PORT must be an integer") from exc
    if not MIN_PORT <= port <= MAX_PORT:
        raise ValueError(f"CEUTIA_PORT must be between {MIN_PORT} and {MAX_PORT}")
    return port


def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        host=_read_host(),
        port=_read_port(),
        code_revision=os.getenv("CEUTIA_CODE_REVISION", "").strip(),
        decision_db=os.getenv("CEUTIA_DECISION_DB", "").strip(),
    )


RUNTIME_CONFIG = load_runtime_config()


@dataclass(frozen=True, slots=True)
class ReadinessState:
    ready: bool
    reason: str | None = None


def _readiness() -> ReadinessState:
    missing = []
    if not RUNTIME_CONFIG.code_revision:
        missing.append("CEUTIA_CODE_REVISION")
    if not RUNTIME_CONFIG.decision_db:
        missing.append("CEUTIA_DECISION_DB")
    if missing:
        return ReadinessState(False, "required decision-runtime configuration missing: " + ", ".join(missing))
    return ReadinessState(True)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    del application
    LOGGER.info("%s starting; version=%s", APP_NAME, APP_VERSION)
    try:
        yield
    except Exception:
        LOGGER.exception("%s lifecycle terminated because of an exception", APP_NAME)
        raise
    finally:
        LOGGER.info("%s shutdown complete", APP_NAME)


app = FastAPI(title=APP_NAME, version=APP_VERSION, description=APP_DESCRIPTION, lifespan=lifespan)


class DecisionScenarioRequest(BaseModel):
    scenario_id: str = Field(min_length=1)
    probability: float = Field(ge=0.0, le=1.0)
    utility: float
    harm: float


class DecisionOptionRequest(BaseModel):
    option_id: str = Field(min_length=1)
    scenarios: list[DecisionScenarioRequest] = Field(min_length=1)
    resource_cost: float = Field(default=0.0, ge=0.0)
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0)


class DecisionEvidenceRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    claim_id: str = Field(min_length=1)
    content_hash: str = Field(min_length=64, max_length=64)
    valid_from: datetime
    valid_until: datetime | None = None
    recorded_from: datetime
    recorded_until: datetime | None = None
    base_weight: float = Field(ge=0.0, le=1.0)
    adversarial_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    contradiction_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    independent_origin: bool = True
    disposition: EvidenceDisposition = EvidenceDisposition.ACCEPT
    provenance_refs: list[str] = Field(min_length=1)
    visibility: InformationVisibility = InformationVisibility.PUBLIC


class DecisionRequest(BaseModel):
    decision_id: str = Field(min_length=1)
    decision_maker: str = Field(min_length=1)
    horizon: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    risk_class: DecisionRisk = DecisionRisk.LOW
    mode: DecisionMode = DecisionMode.ROBUST
    state_refs: list[str] = Field(min_length=1)
    evidence: list[DecisionEvidenceRequest] = Field(min_length=1)
    options: list[DecisionOptionRequest] = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    hypothesis_refs: list[str] = Field(default_factory=list)
    model_refs: list[str] = Field(default_factory=list)
    scenario_refs: list[str] = Field(default_factory=list)
    transformation_refs: list[str] = Field(default_factory=list)
    constraint_refs: list[str] = Field(default_factory=list)
    restricted: bool = False
    output_visibility: InformationVisibility = InformationVisibility.PUBLIC


@app.get("/", tags=["system"], summary="CeutIA service information")
async def root() -> dict[str, str]:
    return {"service": APP_NAME, "version": APP_VERSION, "status": STATUS_RUNNING}


@app.get("/health", tags=["system"], summary="Process liveness check")
async def health() -> dict[str, str]:
    return {"status": STATUS_HEALTHY, "service": APP_NAME, "version": APP_VERSION}


@app.get("/ready", tags=["system"], summary="Application readiness check")
async def ready() -> JSONResponse:
    state = _readiness()
    if state.ready:
        return JSONResponse(status_code=200, content={"status": STATUS_READY, "service": APP_NAME, "version": APP_VERSION})
    return JSONResponse(status_code=503, content={"status": STATUS_NOT_READY, "service": APP_NAME, "version": APP_VERSION, "reason": state.reason})


@app.post("/decision/evaluate", tags=["decision"], summary="Execute the integrated evidence-to-decision lifecycle")
async def evaluate_decision(payload: DecisionRequest) -> dict[str, object]:
    state = _readiness()
    if not state.ready:
        return JSONResponse(status_code=503, content={"status": STATUS_NOT_READY, "reason": state.reason})

    # The API is deliberately fail-closed: incomplete epistemic inputs are not
    # silently converted into a prediction or recommendation.
    for option in payload.options:
        validate_scenario_probabilities([scenario.probability for scenario in option.scenarios])

    store = SQLiteDecisionStore(RUNTIME_CONFIG.decision_db)
    try:
        configuration = ConfigurationProvenance(
            configuration_id="ceutia-decision-runtime",
            version="1",
            source_refs=("environment:decision-runtime",),
            values={"risk_class": payload.risk_class.value, "mode": payload.mode.value},
        )
        lifecycle = DecisionLifecycleEngine(store, code_revision=RUNTIME_CONFIG.code_revision, configuration=configuration)
        evidence: list[DecisionEvidence] = []
        for item in payload.evidence:
            temporal = BitemporalRef(item.valid_from, item.valid_until, item.recorded_from, item.recorded_until, item.evidence_id)
            assessment = EvidenceAssessment(
                evidence_id=item.evidence_id,
                source_id=item.source_id,
                base_weight=item.base_weight,
                adversarial_risk=item.adversarial_risk,
                contradiction_weight=item.contradiction_weight,
                independent_origin=item.independent_origin,
                disposition=item.disposition,
            )
            evidence.append(DecisionEvidence(item.evidence_id, item.source_id, item.claim_id, item.content_hash, tuple(item.provenance_refs), temporal, assessment, item.visibility))
        validate_evidence_set(evidence)

        evidence_store = DecisionEvidenceStore(store)
        for item in evidence:
            evidence_store.record(item)

        options = tuple(
            DecisionOption(
                item.option_id,
                tuple(ScenarioOutcome(s.scenario_id, s.probability, s.utility, s.harm) for s in item.scenarios),
                item.resource_cost,
                item.uncertainty,
            )
            for item in payload.options
        )
        scenario_refs = tuple(payload.scenario_refs) or tuple(s.scenario_id for option in options for s in option.outcomes)
        model_refs = tuple(payload.model_refs)
        model_releases: dict[str, ModelGovernanceRecord] = {}
        if not model_refs:
            deterministic = ModelGovernanceRecord(
                model_id="deterministic:decision-system",
                version="1",
                code_hash=RUNTIME_CONFIG.code_revision,
                data_snapshot_hash=configuration.fingerprint(),
                assumptions=("deterministic decision rules only",),
                valid_from=datetime.now(timezone.utc),
                calibrated=True,
                validation_ref="governance:deterministic-rules",
                calibration_ref="governance:deterministic-rules",
                approval_ref="governance:decision-policy",
            )
            deterministic = replace(deterministic, release_hash=deterministic.fingerprint())
            model_releases[deterministic.model_id] = deterministic
            model_refs = (deterministic.model_id,)

        context = DecisionContext(
            decision_id=payload.decision_id,
            decision_maker=payload.decision_maker,
            horizon=payload.horizon,
            objectives=(DecisionObjective("expected_utility", 1.0, 1),),
            assumptions=tuple(payload.assumptions),
            risk_class=payload.risk_class,
        )
        result = lifecycle.execute(
            context,
            options,
            evidence,
            state_refs=payload.state_refs,
            hypothesis_refs=payload.hypothesis_refs,
            model_refs=model_refs,
            scenario_refs=scenario_refs,
            assumption_refs=payload.assumptions,
            transformation_refs=payload.transformation_refs,
            constraint_refs=payload.constraint_refs,
            purpose=payload.purpose,
            restricted=payload.restricted,
            output_visibility=payload.output_visibility,
            mode=payload.mode,
            model_releases=model_releases,
        )
        return {
            "decision_id": result.decision_id,
            "disposition": result.disposition.value,
            "recommendation": {
                "option_id": result.recommendation.option_id,
                "score": result.recommendation.score,
                "expected_utility": result.recommendation.expected_utility,
                "expected_harm": result.recommendation.expected_harm,
                "maximum_regret": result.recommendation.maximum_regret,
                "reasons": result.recommendation.reasons,
            },
            "control_reason": result.control_reason,
            "audit_event_id": result.audit_event_id,
            "lineage_fingerprint": result.lineage.semantic_fingerprint(),
            "uncertainty": result.uncertainty.value,
            "degraded_reasons": result.degraded_reasons,
        }
    finally:
        store.close()


@app.get("/version", tags=["system"], summary="Application version")
async def version() -> dict[str, str]:
    return {"service": APP_NAME, "version": APP_VERSION}


@app.get("/diagnostics", tags=["system"], summary="Minimal non-sensitive runtime diagnostics")
async def diagnostics() -> dict[str, object]:
    state = _readiness()
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "application": STATUS_RUNNING,
        "liveness": STATUS_HEALTHY,
        "readiness": STATUS_READY if state.ready else STATUS_NOT_READY,
        "runtime": {
            "host_configured": bool(RUNTIME_CONFIG.host),
            "port_configured": MIN_PORT <= RUNTIME_CONFIG.port <= MAX_PORT,
            "code_revision_configured": bool(RUNTIME_CONFIG.code_revision),
            "decision_persistence_configured": bool(RUNTIME_CONFIG.decision_db),
        },
    }


@app.get("/diagnostics/config", tags=["system"], summary="Non-sensitive runtime configuration validation")
async def diagnostics_config() -> dict[str, object]:
    state = _readiness()
    return {
        "status": "valid" if state.ready else "incomplete",
        "host_configured": bool(RUNTIME_CONFIG.host),
        "port_valid": MIN_PORT <= RUNTIME_CONFIG.port <= MAX_PORT,
        "code_revision_configured": bool(RUNTIME_CONFIG.code_revision),
        "decision_persistence_configured": bool(RUNTIME_CONFIG.decision_db),
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    LOGGER.exception("Unhandled exception: method=%s path=%s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "service": APP_NAME, "version": APP_VERSION})


def main() -> None:
    import uvicorn
    uvicorn.run("app.main:app", host=RUNTIME_CONFIG.host, port=RUNTIME_CONFIG.port)


if __name__ == "__main__":
    main()
