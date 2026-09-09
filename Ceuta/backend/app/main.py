"""
CeutIA — Canonical Backend Application Entrypoint
===================================================

This module is the canonical application boundary for the CeutIA backend.

It is responsible for:

- creating the FastAPI application;
- defining application metadata;
- validating basic runtime configuration;
- defining deterministic startup and shutdown behaviour;
- exposing non-sensitive system endpoints;
- separating liveness from readiness;
- exposing minimal diagnostics;
- protecting clients from internal exception disclosure;
- providing the Python console entrypoint;
- providing direct-module execution compatibility.

It is deliberately NOT responsible for implementing the analytical
subsystems themselves.

The following capabilities belong to their own validated modules/services:

- evidence ingestion;
- official-source monitoring;
- provenance;
- epistemic validation;
- adversarial validation;
- metrics;
- risk models;
- dynamic-system models;
- information classification;
- public/private information boundaries;
- PostgreSQL persistence;
- Redis/cache;
- authentication;
- authorization;
- operational decision support.

Those capabilities must be integrated only after their individual
contracts and dependencies have been validated.

Startup must therefore remain deterministic and side-effect controlled.
A failure in one unfinished analytical subsystem must not prevent the
application entrypoint from being imported and health-checked.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ============================================================================
# APPLICATION IDENTITY
# ============================================================================

APP_NAME = "CeutIA"

APP_VERSION = "0.1.0"

APP_DESCRIPTION = (
    "Evidence-based territorial intelligence, knowledge and "
    "early-warning platform for Ceuta."
)


# ============================================================================
# APPLICATION STATES
# ============================================================================

STATUS_RUNNING = "running"

STATUS_HEALTHY = "healthy"

STATUS_NOT_READY = "not_ready"

STATUS_READY = "ready"


# ============================================================================
# DEFAULT RUNTIME CONFIGURATION
# ============================================================================

DEFAULT_HOST = "0.0.0.0"

DEFAULT_PORT = 8000

MIN_PORT = 1

MAX_PORT = 65535


# ============================================================================
# LOGGING
# ============================================================================

LOGGER = logging.getLogger(APP_NAME)


def _configure_logging() -> None:
    """
    Configure a minimal application logger.

    The function intentionally does not overwrite handlers installed by
    an external process manager or logging framework.
    """
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s %(levelname)s "
                "%(name)s %(message)s"
            ),
        )


_configure_logging()


# ============================================================================
# RUNTIME CONFIGURATION
# ============================================================================

@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """
    Validated process-level configuration.

    This configuration contains only values required to start the
    HTTP application. Database, Redis and analytical configuration
    belong to their respective service layers.
    """

    host: str

    port: int


def _read_host() -> str:
    """
    Read and validate CEUTIA_HOST.

    An explicitly empty value is rejected rather than silently converted
    into an invalid server configuration.
    """
    host = os.getenv(
        "CEUTIA_HOST",
        DEFAULT_HOST,
    ).strip()

    if not host:
        raise ValueError(
            "CEUTIA_HOST cannot be empty"
        )

    return host


def _read_port() -> int:
    """
    Read and validate CEUTIA_PORT.

    The value must be a decimal integer in the valid TCP port range.
    """
    raw_port = os.getenv(
        "CEUTIA_PORT",
        str(DEFAULT_PORT),
    ).strip()

    if not raw_port:
        raise ValueError(
            "CEUTIA_PORT cannot be empty"
        )

    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError(
            "CEUTIA_PORT must be an integer"
        ) from exc

    if not MIN_PORT <= port <= MAX_PORT:
        raise ValueError(
            f"CEUTIA_PORT must be between "
            f"{MIN_PORT} and {MAX_PORT}"
        )

    return port


def load_runtime_config() -> RuntimeConfig:
    """
    Construct validated runtime configuration.

    This function is intentionally deterministic and has no network,
    database or filesystem side effects.
    """
    return RuntimeConfig(
        host=_read_host(),
        port=_read_port(),
    )


RUNTIME_CONFIG = load_runtime_config()


# ============================================================================
# READINESS STATE
# ============================================================================

@dataclass(frozen=True, slots=True)
class ReadinessState:
    """
    Explicit application readiness state.

    Liveness and readiness are deliberately separate concepts.

    A process can be alive while its dependency graph is not yet ready.
    """

    ready: bool

    reason: str | None = None


_INITIAL_READINESS = ReadinessState(
    ready=False,
    reason=(
        "Validated database, cache, monitoring and analytical "
        "dependencies are not yet connected."
    ),
)


# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    """
    Manage application startup and shutdown.

    No external dependency is initialized here yet.

    This is intentional.

    PostgreSQL, Redis, source monitoring, analytical models,
    epistemic validation and other subsystems must first expose
    explicit and validated lifecycle contracts before they are
    connected to application startup.

    The application object is accepted as required by FastAPI's
    lifespan protocol. It is intentionally not mutated here.
    """
    del application

    LOGGER.info(
        "%s starting; version=%s",
        APP_NAME,
        APP_VERSION,
    )

    try:
        yield
    except Exception:
        LOGGER.exception(
            "%s lifecycle terminated because of an exception",
            APP_NAME,
        )
        raise
    finally:
        LOGGER.info(
            "%s shutdown complete",
            APP_NAME,
        )


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get(
    "/",
    tags=["system"],
    summary="CeutIA service information",
)
async def root() -> dict[str, str]:
    """
    Return non-sensitive service metadata.

    This endpoint does not access:

    - PostgreSQL;
    - Redis;
    - external sources;
    - analytical models;
    - private intelligence;
    - personal data.
    """
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": STATUS_RUNNING,
    }


# ============================================================================
# LIVENESS ENDPOINT
# ============================================================================

@app.get(
    "/health",
    tags=["system"],
    summary="Process liveness check",
)
async def health() -> dict[str, str]:
    """
    Return process-level liveness.

    HTTP success means that the FastAPI process has been successfully
    imported and is capable of serving requests.

    It does NOT assert that:

    - PostgreSQL is available;
    - Redis is available;
    - source ingestion is working;
    - monitoring is working;
    - analytical models are available;
    - predictions are validated;
    - the system is operationally ready.
    """
    return {
        "status": STATUS_HEALTHY,
        "service": APP_NAME,
        "version": APP_VERSION,
    }


# ============================================================================
# READINESS ENDPOINT
# ============================================================================

@app.get(
    "/ready",
    tags=["system"],
    summary="Application readiness check",
)
async def ready() -> JSONResponse:
    """
    Report validated application readiness.

    Until the dependency graph has been connected and validated,
    CeutIA must explicitly report NOT READY.

    This prevents orchestration systems from interpreting a merely
    alive Python process as a fully operational intelligence platform.
    """
    state = _INITIAL_READINESS

    if state.ready:
        return JSONResponse(
            status_code=200,
            content={
                "status": STATUS_READY,
                "service": APP_NAME,
                "version": APP_VERSION,
            },
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


# ============================================================================
# VERSION ENDPOINT
# ============================================================================

@app.get(
    "/version",
    tags=["system"],
    summary="Application version",
)
async def version() -> dict[str, str]:
    """
    Return the currently deployed CeutIA application version.
    """
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
    }


# ============================================================================
# DIAGNOSTICS ENDPOINT
# ============================================================================

@app.get(
    "/diagnostics",
    tags=["system"],
    summary="Minimal non-sensitive runtime diagnostics",
)
async def diagnostics() -> dict[str, object]:
    """
    Return deliberately limited runtime diagnostics.

    Information intentionally excluded:

    - environment variables;
    - credentials;
    - database URLs;
    - Redis URLs;
    - filesystem paths;
    - process IDs;
    - host information;
    - private intelligence;
    - personal information;
    - stack traces;
    - model internals.

    This endpoint is therefore suitable for basic operational inspection
    without becoming an information-disclosure interface.
    """
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "application": STATUS_RUNNING,
        "liveness": STATUS_HEALTHY,
        "readiness": STATUS_NOT_READY,
        "runtime": {
            "host_configured": bool(
                RUNTIME_CONFIG.host
            ),
            "port_configured": (
                MIN_PORT
                <= RUNTIME_CONFIG.port
                <= MAX_PORT
            ),
        },
    }


# ============================================================================
# CONFIGURATION VALIDATION ENDPOINT
# ============================================================================

@app.get(
    "/diagnostics/config",
    tags=["system"],
    summary="Non-sensitive runtime configuration validation",
)
async def diagnostics_config() -> dict[str, object]:
    """
    Report whether the process-level HTTP configuration is valid.

    Only boolean/status information is returned.

    Actual configuration values are never exposed.
    """
    return {
        "status": "valid",
        "host_configured": bool(
            RUNTIME_CONFIG.host
        ),
        "port_valid": (
            MIN_PORT
            <= RUNTIME_CONFIG.port
            <= MAX_PORT
        ),
    }


# ============================================================================
# CONTROLLED EXCEPTION HANDLER
# ============================================================================

@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected application exceptions.

    The complete exception is retained in server-side logs but is not
    returned to the client.

    This prevents accidental disclosure of:

    - Python stack traces;
    - filesystem paths;
    - SQL/database details;
    - credentials;
    - implementation details;
    - internal intelligence;
    - analytical information.
    """
    LOGGER.exception(
        "Unhandled exception: method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "service": APP_NAME,
            "version": APP_VERSION,
        },
    )


# ============================================================================
# CONSOLE ENTRYPOINT
# ============================================================================

def main() -> None:
    """
    Start the CeutIA API using Uvicorn.

    This function satisfies the console-script contract declared by
    pyproject.toml:

        ceutia = "app.main:main"

    The FastAPI application remains directly available as:

        app.main:app
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=RUNTIME_CONFIG.host,
        port=RUNTIME_CONFIG.port,
    )


# ============================================================================
# DIRECT MODULE EXECUTION
# ============================================================================

if __name__ == "__main__":
    main()