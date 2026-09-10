"""CeutIA canonical FastAPI application entrypoint."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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


def _read_host() -> str:
    host = os.getenv("CEUTIA_HOST", DEFAULT_HOST).strip()
    if not host:
        raise ValueError("CEUTIA_HOST cannot be empty")
    return host


def _read_port() -> int:
    raw_port = os.getenv("CEUTIA_PORT", str(DEFAULT_PORT)).strip()
    if not raw_port:
        raise ValueError("CEUTIA_PORT cannot be empty")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("CEUTIA_PORT must be an integer") from exc
    if not MIN_PORT <= port <= MAX_PORT:
        raise ValueError(f"CEUTIA_PORT must be between {MIN_PORT} and {MAX_PORT}")
    return port


def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(host=_read_host(), port=_read_port())


RUNTIME_CONFIG = load_runtime_config()


@dataclass(frozen=True, slots=True)
class ReadinessState:
    ready: bool
    reason: str | None = None


_INITIAL_READINESS = ReadinessState(
    ready=False,
    reason="Validated database, cache, monitoring and analytical dependencies are not yet connected.",
)


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


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)


@app.get("/", tags=["system"], summary="CeutIA service information")
async def root() -> dict[str, str]:
    return {"service": APP_NAME, "version": APP_VERSION, "status": STATUS_RUNNING}


@app.get("/health", tags=["system"], summary="Process liveness check")
async def health() -> dict[str, str]:
    return {"status": STATUS_HEALTHY, "service": APP_NAME, "version": APP_VERSION}


@app.get("/ready", tags=["system"], summary="Application readiness check")
async def ready() -> JSONResponse:
    state = _INITIAL_READINESS
    if state.ready:
        return JSONResponse(
            status_code=200,
            content={"status": STATUS_READY, "service": APP_NAME, "version": APP_VERSION},
        )
    return JSONResponse(
        status_code=503,
        content={
            "status": STATUS_NOT_READY,
            "service": APP_NAME,
            "version": APP_VERSION,
            "reason": state.reason,
        },
    )


@app.get("/version", tags=["system"], summary="Application version")
async def version() -> dict[str, str]:
    return {"service": APP_NAME, "version": APP_VERSION}


@app.get("/diagnostics", tags=["system"], summary="Minimal non-sensitive runtime diagnostics")
async def diagnostics() -> dict[str, object]:
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "application": STATUS_RUNNING,
        "liveness": STATUS_HEALTHY,
        "readiness": STATUS_NOT_READY,
        "runtime": {
            "host_configured": bool(RUNTIME_CONFIG.host),
            "port_configured": MIN_PORT <= RUNTIME_CONFIG.port <= MAX_PORT,
        },
    }


@app.get("/diagnostics/config", tags=["system"], summary="Non-sensitive runtime configuration validation")
async def diagnostics_config() -> dict[str, object]:
    return {
        "status": "valid",
        "host_configured": bool(RUNTIME_CONFIG.host),
        "port_valid": MIN_PORT <= RUNTIME_CONFIG.port <= MAX_PORT,
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    LOGGER.exception(
        "Unhandled exception: method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "service": APP_NAME, "version": APP_VERSION},
    )


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=RUNTIME_CONFIG.host, port=RUNTIME_CONFIG.port)


if __name__ == "__main__":
    main()
