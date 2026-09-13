"""Adversarial regression tests for the executable security boundary."""

from __future__ import annotations

import base64
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.security.enforcement import (
    Action,
    ActionClass,
    AuthorizationError,
    Capability,
    EnforcementState,
    SecurityEnforcer,
)


class Clock:
    def __init__(self, value: int = 1_000) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def _setup(monkeypatch: pytest.MonkeyPatch) -> tuple[SecurityEnforcer, Clock, Ed25519PrivateKey]:
    clock = Clock()
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    monkeypatch.setenv("CEUTIA_OWNER_SIGNING_PUBLIC_KEY", public)
    monkeypatch.setenv("CEUTIA_HIGH_IMPACT_APPROVAL_EVIDENCE", "human-approved-once")
    return SecurityEnforcer(clock=clock), clock, private


def _capability(
    private: Ed25519PrivateKey,
    *,
    principal: str = "agent:test",
    action_class: ActionClass = ActionClass.ANALYZE,
    operation: str = "read",
    resource: str = "source:1",
    destination: str = "",
    data_class: str = "public",
    parameters_digest: str = "",
    issued_at: int = 1_000,
    expires_at: int = 1_060,
    token_id: str = "token-1",
    nonce: str = "nonce-1",
) -> Capability:
    capability = Capability(
        token_id=token_id,
        owner_id="drsalvadorroman-beep",
        principal=principal,
        action_class=action_class,
        operation=operation,
        resource=resource,
        destination=destination,
        data_class=data_class,
        parameters_digest=parameters_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        nonce=nonce,
        signature=b"",
    )
    return Capability(
        token_id=capability.token_id,
        owner_id=capability.owner_id,
        principal=capability.principal,
        action_class=capability.action_class,
        operation=capability.operation,
        resource=capability.resource,
        destination=capability.destination,
        data_class=capability.data_class,
        parameters_digest=capability.parameters_digest,
        issued_at=capability.issued_at,
        expires_at=capability.expires_at,
        nonce=capability.nonce,
        signature=private.sign(capability.canonical()),
    )


def _action(cap: Capability) -> Action:
    return Action(
        action_id="action-1",
        principal=cap.principal,
        action_class=cap.action_class,
        operation=cap.operation,
        resource=cap.resource,
        destination=cap.destination,
        data_class=cap.data_class,
        parameters_digest=cap.parameters_digest,
    )


def test_valid_signed_capability_authorizes_exact_action(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    cap = _capability(private)
    enforcer.authorize(_action(cap), cap)


def test_missing_owner_key_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    monkeypatch.delenv("CEUTIA_OWNER_SIGNING_PUBLIC_KEY")
    cap = _capability(private)
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(cap), cap)


def test_tampered_capability_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    cap = _capability(private)
    tampered = Capability(
        token_id=cap.token_id,
        owner_id=cap.owner_id,
        principal=cap.principal,
        action_class=cap.action_class,
        operation="delete",
        resource=cap.resource,
        destination=cap.destination,
        data_class=cap.data_class,
        parameters_digest=cap.parameters_digest,
        issued_at=cap.issued_at,
        expires_at=cap.expires_at,
        nonce=cap.nonce,
        signature=cap.signature,
    )
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(tampered), tampered)


def test_expired_capability_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, clock, private = _setup(monkeypatch)
    cap = _capability(private, expires_at=1_001)
    clock.value = 1_001
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(cap), cap)


def test_capability_cannot_be_reused(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    cap = _capability(private)
    enforcer.authorize(_action(cap), cap)
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(cap), cap)


def test_revocation_blocks_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    cap = _capability(private)
    enforcer.revoke(cap.token_id)
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(cap), cap)


def test_incident_state_blocks_even_valid_capability(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    cap = _capability(private)
    enforcer.enter_incident()
    assert enforcer.state == EnforcementState.INCIDENT
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(cap), cap)


def test_parameter_digest_is_part_of_authorization(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    digest = Action.digest_parameters({"destination": "safe"})
    cap = _capability(private, parameters_digest=digest)
    action = Action(
        action_id="action-1",
        principal=cap.principal,
        action_class=cap.action_class,
        operation=cap.operation,
        resource=cap.resource,
        parameters_digest=Action.digest_parameters({"destination": "different"}),
    )
    with pytest.raises(AuthorizationError):
        enforcer.authorize(action, cap)


def test_high_impact_action_requires_independent_human_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enforcer, _, private = _setup(monkeypatch)
    monkeypatch.delenv("CEUTIA_HIGH_IMPACT_APPROVAL_EVIDENCE")
    cap = _capability(private, action_class=ActionClass.PUBLICATION)
    with pytest.raises(AuthorizationError):
        enforcer.authorize(_action(cap), cap)


def test_signed_document_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    enforcer, _, private = _setup(monkeypatch)
    cap = _capability(private)
    document = {
        "token_id": cap.token_id,
        "owner_id": cap.owner_id,
        "principal": cap.principal,
        "action_class": cap.action_class.value,
        "operation": cap.operation,
        "resource": cap.resource,
        "destination": cap.destination,
        "data_class": cap.data_class,
        "parameters_digest": cap.parameters_digest,
        "issued_at": cap.issued_at,
        "expires_at": cap.expires_at,
        "nonce": cap.nonce,
        "signature": base64.urlsafe_b64encode(cap.signature).decode().rstrip("="),
    }
    restored = Capability.from_signed_document(json.loads(json.dumps(document)))
    enforcer.authorize(_action(restored), restored)
