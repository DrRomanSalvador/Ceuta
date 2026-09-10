"""Executable fail-closed authorization boundary for CeutIA.

The model/runtime never creates authorization. A separate owner-controlled
issuer signs short-lived capability tokens; this process holds only the
issuer's public key and verifies the exact requested action at execution time.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

OWNER_ID = "drsalvadorroman-beep"


class AuthorizationError(PermissionError):
    """Raised whenever an action cannot be independently authorized."""


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


HIGH_IMPACT = frozenset(ActionClass) - frozenset({ActionClass.READ, ActionClass.ANALYZE})


@dataclass(frozen=True, slots=True)
class Action:
    action_id: str
    principal: str
    action_class: ActionClass
    operation: str
    resource: str
    destination: str = ""
    data_class: str = "public"
    parameters_digest: str = ""

    @staticmethod
    def digest_parameters(parameters: Mapping[str, Any]) -> str:
        encoded = json.dumps(parameters, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(encoded).hexdigest()

    def canonical(self) -> bytes:
        return _canonical(
            {
                "action_id": self.action_id,
                "principal": self.principal,
                "action_class": self.action_class.value,
                "operation": self.operation,
                "resource": self.resource,
                "destination": self.destination,
                "data_class": self.data_class,
                "parameters_digest": self.parameters_digest,
            }
        )


@dataclass(frozen=True, slots=True)
class Capability:
    token_id: str
    owner_id: str
    principal: str
    action_class: ActionClass
    operation: str
    resource: str
    destination: str
    data_class: str
    parameters_digest: str
    issued_at: int
    expires_at: int
    nonce: str
    signature: bytes

    def canonical(self) -> bytes:
        return _canonical(
            {
                "token_id": self.token_id,
                "owner_id": self.owner_id,
                "principal": self.principal,
                "action_class": self.action_class.value,
                "operation": self.operation,
                "resource": self.resource,
                "destination": self.destination,
                "data_class": self.data_class,
                "parameters_digest": self.parameters_digest,
                "issued_at": self.issued_at,
                "expires_at": self.expires_at,
                "nonce": self.nonce,
            }
        )

    @classmethod
    def from_signed_document(cls, document: Mapping[str, Any]) -> "Capability":
        try:
            return cls(
                token_id=str(document["token_id"]),
                owner_id=str(document["owner_id"]),
                principal=str(document["principal"]),
                action_class=ActionClass(str(document["action_class"])),
                operation=str(document["operation"]),
                resource=str(document["resource"]),
                destination=str(document.get("destination", "")),
                data_class=str(document.get("data_class", "public")),
                parameters_digest=str(document.get("parameters_digest", "")),
                issued_at=int(document["issued_at"]),
                expires_at=int(document["expires_at"]),
                nonce=str(document["nonce"]),
                signature=_b64decode(str(document["signature"])),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthorizationError("Malformed capability") from exc


def _canonical(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _b64decode(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value.encode("ascii") + b"=" * (-len(value) % 4))
    except (ValueError, UnicodeEncodeError) as exc:
        raise AuthorizationError("Malformed signature encoding") from exc


class SecurityEnforcer:
    """Independent runtime gate. Default is deny unless all checks pass."""

    def __init__(self, *, owner_id: str = OWNER_ID, clock: Any = time.time) -> None:
        if owner_id != OWNER_ID:
            raise AuthorizationError("Invalid human owner principal")
        self._owner_id = owner_id
        self._clock = clock
        self._state = EnforcementState.NORMAL
        self._revoked_tokens: set[str] = set()
        self._used_nonces: set[str] = set()

    @property
    def state(self) -> EnforcementState:
        return self._state

    def restrict(self) -> None:
        self._state = EnforcementState.RESTRICTED

    def enter_incident(self) -> None:
        self._state = EnforcementState.INCIDENT

    def contain(self) -> None:
        self._state = EnforcementState.CONTAINED

    def begin_recovery(self) -> None:
        self._state = EnforcementState.RECOVERY

    def verify_recovery(self) -> None:
        self._state = EnforcementState.VERIFIED

    def revoke(self, token_id: str) -> None:
        self._revoked_tokens.add(token_id)

    def _public_key(self) -> Ed25519PublicKey:
        pem = os.environ.get("CEUTIA_OWNER_SIGNING_PUBLIC_KEY", "").encode("utf-8")
        if not pem:
            raise AuthorizationError("Owner signing public key is not provisioned")
        try:
            key = serialization.load_pem_public_key(pem)
        except ValueError as exc:
            raise AuthorizationError("Invalid owner signing public key") from exc
        if not isinstance(key, Ed25519PublicKey):
            raise AuthorizationError("Owner signing key must be Ed25519")
        return key

    def verify_capability(self, capability: Capability) -> None:
        if capability.owner_id != self._owner_id:
            raise AuthorizationError("Capability owner is invalid")
        if capability.token_id in self._revoked_tokens:
            raise AuthorizationError("Capability has been revoked")
        if capability.nonce in self._used_nonces:
            raise AuthorizationError("Capability nonce has already been used")
        now = int(self._clock())
        if capability.issued_at > now or capability.expires_at <= now:
            raise AuthorizationError("Capability is outside its validity window")
        if capability.expires_at - capability.issued_at > 900:
            raise AuthorizationError("Capability lifetime exceeds maximum")
        try:
            self._public_key().verify(capability.signature, capability.canonical())
        except Exception as exc:
            raise AuthorizationError("Capability signature is invalid") from exc

    def authorize(self, action: Action, capability: Capability) -> None:
        if self._state not in {EnforcementState.NORMAL, EnforcementState.VERIFIED}:
            raise AuthorizationError(f"Execution denied in security state {self._state.value}")
        if not action.action_id or not action.principal:
            raise AuthorizationError("Action identity and principal are required")
        self.verify_capability(capability)
        if (
            capability.principal != action.principal
            or capability.action_class != action.action_class
            or capability.operation != action.operation
            or capability.resource != action.resource
            or capability.destination != action.destination
            or capability.data_class != action.data_class
            or capability.parameters_digest != action.parameters_digest
        ):
            raise AuthorizationError("Capability does not authorize the exact requested action")
        if action.action_class in HIGH_IMPACT and not os.environ.get("CEUTIA_HIGH_IMPACT_APPROVAL_EVIDENCE"):
            raise AuthorizationError("Independent human approval evidence is required for high-impact action")
        self._used_nonces.add(capability.nonce)

    def execute(self, action: Action, capability: Capability, operation: Any) -> Any:
        """Execute only after an independent authorization decision."""
        self.authorize(action, capability)
        if not callable(operation):
            raise AuthorizationError("Execution target is not callable")
        return operation()
