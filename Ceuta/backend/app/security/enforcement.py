"""Executable security boundary for CeutIA consequential actions.

This module is deliberately fail-closed. Model output, retrieved content,
memory, agent consensus and tool availability can propose an action but can
never authorize one. Authorization is represented by an explicit capability
object and checked again at execution time.

The module is a local enforcement primitive, not a claim of complete system
security. Host, cloud, GitHub, network, identity-provider and hardware
controls remain part of the external trust boundary.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

OWNER_ID = "drsalvadorroman-beep"


class AuthorizationError(PermissionError):
    """Raised whenever a consequential action cannot be authorized."""


class EnforcementState(str, Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    INCIDENT = "incident"
    CONTAINED = "contained"
    RECOVERY = "recovery"
    VERIFIED = "verified"


class ActionClass(str, Enum):
    READ = "read"
    ANALYZE = "analyze"
    INTERNAL_WRITE = "internal_write"
    EXTERNAL_WRITE = "external_write"
    PUBLICATION = "publication"
    OWNER_REPRESENTATION = "owner_representation"
    FINANCIAL = "financial"
    LEGAL = "legal"
    CLINICAL = "clinical"
    SENSITIVE_DATA = "sensitive_data"
    DESTRUCTIVE = "destructive"
    SECURITY_CONTROL = "security_control"
    DUAL_USE = "dual_use"
    CONFLICT_OPERATIONAL = "conflict_operational"


HIGH_IMPACT = frozenset(
    {
        ActionClass.EXTERNAL_WRITE,
        ActionClass.PUBLICATION,
        ActionClass.OWNER_REPRESENTATION,
        ActionClass.FINANCIAL,
        ActionClass.LEGAL,
        ActionClass.CLINICAL,
        ActionClass.SENSITIVE_DATA,
        ActionClass.DESTRUCTIVE,
        ActionClass.SECURITY_CONTROL,
        ActionClass.DUAL_USE,
        ActionClass.CONFLICT_OPERATIONAL,
    }
)


@dataclass(frozen=True, slots=True)
class Action:
    """Canonical description of one proposed operation."""

    action_id: str
    principal: str
    action_class: ActionClass
    operation: str
    resource: str
    destination: str = ""
    data_class: str = "public"
    parameters_digest: str = ""

    def canonical(self) -> bytes:
        payload = {
            "action_id": self.action_id,
            "principal": self.principal,
            "action_class": self.action_class.value,
            "operation": self.operation,
            "resource": self.resource,
            "destination": self.destination,
            "data_class": self.data_class,
            "parameters_digest": self.parameters_digest,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True, slots=True)
class Capability:
    """Explicit, bounded authorization. It is not inferred from model output."""

    token_id: str
    owner_id: str
    principal: str
    action_class: ActionClass
    operation: str
    resource: str
    destination: str
    data_class: str
    issued_at: int
    expires_at: int
    nonce: str
    signature: str

    def canonical(self) -> bytes:
        payload = {
            "token_id": self.token_id,
            "owner_id": self.owner_id,
            "principal": self.principal,
            "action_class": self.action_class.value,
            "operation": self.operation,
            "resource": self.resource,
            "destination": self.destination,
            "data_class": self.data_class,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


class SecurityEnforcer:
    """Fail-closed action authorization and revocation boundary.

    The owner signing secret is intentionally never generated, persisted or
    exposed by this module. It must be provisioned outside the model/runtime
    through a protected secret mechanism. Absence of the secret means that
    consequential actions remain denied.
    """

    def __init__(self, *, owner_id: str = OWNER_ID, clock: Any = time.time) -> None:
        if owner_id != OWNER_ID:
            raise AuthorizationError("Only the configured human owner may be the owner principal")
        self._owner_id = owner_id
        self._clock = clock
        self._state = EnforcementState.NORMAL
        self._revoked_tokens: set[str] = set()
        self._used_nonces: set[str] = set()

    @property
    def state(self) -> EnforcementState:
        return self._state

    def enter_incident(self) -> None:
        self._state = EnforcementState.INCIDENT

    def restrict(self) -> None:
        self._state = EnforcementState.RESTRICTED

    def contain(self) -> None:
        self._state = EnforcementState.CONTAINED

    def begin_recovery(self) -> None:
        self._state = EnforcementState.RECOVERY

    def verify_recovery(self) -> None:
        self._state = EnforcementState.VERIFIED

    def revoke(self, token_id: str) -> None:
        self._revoked_tokens.add(token_id)

    @staticmethod
    def digest_parameters(parameters: Mapping[str, Any]) -> str:
        encoded = json.dumps(parameters, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(encoded).hexdigest()

    def _secret(self) -> bytes:
        value = os.environ.get("CEUTIA_OWNER_AUTH_SECRET", "")
        if not value:
            raise AuthorizationError("Owner authorization secret is not provisioned")
        return value.encode()

    def issue_capability_for_owner(
        self,
        *,
        principal: str,
        action_class: ActionClass,
        operation: str,
        resource: str,
        destination: str = "",
        data_class: str = "public",
        ttl_seconds: int = 60,
    ) -> Capability:
        """Create a bounded capability only for the external owner authority path.

        This method is intended for an owner-controlled authorization service,
        not for an AI agent. Callers must keep the signing secret outside model
        context. High-impact actions should additionally require the owner's
        separate approval mechanism before this function is invoked.
        """
        if self._state in {EnforcementState.INCIDENT, EnforcementState.CONTAINED}:
            raise AuthorizationError("Capability issuance is disabled during incident containment")
        if not principal or ttl_seconds <= 0 or ttl_seconds > 900:
            raise AuthorizationError("Invalid capability scope or lifetime")
        if action_class in HIGH_IMPACT and not os.environ.get("CEUTIA_HUMAN_APPROVAL_NONCE"):
            raise AuthorizationError("Explicit human approval is required for high-impact actions")

        now = int(self._clock())
        token = Capability(
            token_id=secrets.token_urlsafe(18),
            owner_id=self._owner_id,
            principal=principal,
            action_class=action_class,
            operation=operation,
            resource=resource,
            destination=destination,
            data_class=data_class,
            issued_at=now,
            expires_at=now + ttl_seconds,
            nonce=secrets.token_urlsafe(24),
            signature="",
        )
        signature = hmac.new(self._secret(), token.canonical(), hashlib.sha256).hexdigest()
        return Capability(**{**token.__dict__, "signature": signature})

    def authorize(self, action: Action, capability: Capability) -> None:
        """Authorize one exact action; any mismatch is denied."""
        if self._state not in {EnforcementState.NORMAL, EnforcementState.VERIFIED}:
            raise AuthorizationError(f"Execution denied while security state is {self._state.value}")
        if capability.token_id in self._revoked_tokens:
            raise AuthorizationError("Capability has been revoked")
        if capability.owner_id != self._owner_id:
            raise AuthorizationError("Capability owner is invalid")
        if capability.principal != action.principal:
            raise AuthorizationError("Principal mismatch")
        if capability.action_class != action.action_class:
            raise AuthorizationError("Action-class mismatch")
        if capability.operation != action.operation:
            raise AuthorizationError("Operation mismatch")
        if capability.resource != action.resource:
            raise AuthorizationError("Resource mismatch")
        if capability.destination != action.destination:
            raise AuthorizationError("Destination mismatch")
        if capability.data_class != action.data_class:
            raise AuthorizationError("Data-class mismatch")
        now = int(self._clock())
        if now < capability.issued_at or now >= capability.expires_at:
            raise AuthorizationError("Capability is outside its validity window")
        if capability.nonce in self._used_nonces:
            raise AuthorizationError("Capability nonce has already been used")

        expected = hmac.new(self._secret(), capability.canonical(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, capability.signature):
            raise AuthorizationError("Invalid capability signature")

        if action.action_id == "":
            raise AuthorizationError("Action identity is required")
        self._used_nonces.add(capability.nonce)

    def execute(self, action: Action, capability: Capability, operation: Any) -> Any:
        """Execute only after an independent authorization decision."""
        self.authorize(action, capability)
        if not callable(operation):
            raise AuthorizationError("Execution target is not callable")
        return operation()
