from __future__ import annotations

import base64
import os
import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from app.security.external_trust import (
    ExternalAttestation,
    ExternalTrustError,
    ExternalTrustVerifier,
)


def configure(private: Ed25519PrivateKey) -> None:
    public = private.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
    os.environ["CEUTIA_EXTERNAL_TRUST_PUBLIC_KEY"] = public
    os.environ["CEUTIA_EXTERNAL_TRUST_AUTHORITY"] = "external-owner-authority"
    os.environ["CEUTIA_EXTERNAL_TRUST_KEY_ID"] = "owner-key-1"


def make_attestation(private: Ed25519PrivateKey, *, artifact: str, control: str, policy: str) -> ExternalAttestation:
    now = int(time.time())
    unsigned = ExternalAttestation(
        authority="external-owner-authority",
        key_id="owner-key-1",
        artifact_digest=artifact,
        control_plane_digest=control,
        policy_version=policy,
        issued_at=now - 1,
        expires_at=now + 60,
        nonce="0123456789abcdef",
        signature="placeholder",
    )
    signature = base64.b64encode(private.sign(unsigned.unsigned_payload())).decode()
    return ExternalAttestation(**{**unsigned.__dict__, "signature": signature})


def test_valid_external_attestation() -> None:
    private = Ed25519PrivateKey.generate()
    configure(private)
    verifier = ExternalTrustVerifier()
    attestation = make_attestation(private, artifact="a" * 64, control="b" * 64, policy="2026-09-10")
    verifier.verify(attestation, artifact_digest="a" * 64, control_plane_digest="b" * 64, policy_version="2026-09-10")


def test_missing_external_root_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CEUTIA_EXTERNAL_TRUST_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("CEUTIA_EXTERNAL_TRUST_AUTHORITY", raising=False)
    monkeypatch.delenv("CEUTIA_EXTERNAL_TRUST_KEY_ID", raising=False)
    with pytest.raises(ExternalTrustError):
        ExternalTrustVerifier()


def test_tampered_artifact_is_rejected() -> None:
    private = Ed25519PrivateKey.generate()
    configure(private)
    verifier = ExternalTrustVerifier()
    attestation = make_attestation(private, artifact="a" * 64, control="b" * 64, policy="2026-09-10")
    with pytest.raises(ExternalTrustError):
        verifier.verify(attestation, artifact_digest="c" * 64, control_plane_digest="b" * 64, policy_version="2026-09-10")


def test_tampered_signature_is_rejected() -> None:
    private = Ed25519PrivateKey.generate()
    configure(private)
    verifier = ExternalTrustVerifier()
    attestation = make_attestation(private, artifact="a" * 64, control="b" * 64, policy="2026-09-10")
    bad = ExternalAttestation(**{**attestation.__dict__, "signature": base64.b64encode(b"bad").decode()})
    with pytest.raises(ExternalTrustError):
        verifier.verify(bad, artifact_digest="a" * 64, control_plane_digest="b" * 64, policy_version="2026-09-10")
