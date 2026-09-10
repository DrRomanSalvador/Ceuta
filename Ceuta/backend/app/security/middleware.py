"""HTTP enforcement boundary for consequential CeutIA API operations."""

from __future__ import annotations

import json

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from .enforcement import Action, ActionClass, AuthorizationError, Capability, SecurityEnforcer


PUBLIC_SYSTEM_PATHS = frozenset({
    "/",
    "/health",
    "/ready",
    "/version",
    "/diagnostics",
    "/diagnostics/config",
})


class SecurityActionMiddleware(BaseHTTPMiddleware):
    """Require an independently signed capability for every non-system route."""

    def __init__(self, app: object, enforcer: SecurityEnforcer) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._enforcer = enforcer

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_SYSTEM_PATHS:
            return await call_next(request)

        try:
            document_header = request.headers.get("x-ceutia-capability")
            if not document_header:
                raise AuthorizationError("Signed capability is required")
            document = json.loads(document_header)
            capability = Capability.from_signed_document(document)
            action_class = ActionClass(request.headers["x-ceutia-action-class"])
            parameters_digest = request.headers.get("x-ceutia-parameters-digest", "")
            action = Action(
                action_id=request.headers["x-ceutia-action-id"],
                principal=request.headers["x-ceutia-principal"],
                action_class=action_class,
                operation=request.headers["x-ceutia-operation"],
                resource=request.headers["x-ceutia-resource"],
                destination=request.headers.get("x-ceutia-destination", ""),
                data_class=request.headers.get("x-ceutia-data-class", "public"),
                parameters_digest=parameters_digest,
            )
            self._enforcer.authorize(action, capability)
        except (AuthorizationError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            return JSONResponse(
                status_code=403,
                content={"error": "authorization_denied", "detail": str(exc)},
            )

        return await call_next(request)
