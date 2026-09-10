"""Fail-closed verification of authorization attestations issued outside CeutIA.

The runtime contains only the external authority's public key. It cannot mint
or broaden attestations. This module deliberately does not provide an issuer.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key


class ExternalTrustError(RuntimeError):
    """Raised whenever external trust cannot be established."""


@dataclass(frozen=True)
class ExternalAttestation:
    authority: str
    key_id: str
    artifact_digest: str
    control_plane_digest: str
    policy_version: str
    issued_at: int
    expires_at: int
    nonce: str
    signature: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ExternalAttestation":
        fields = {
            "authority": str(value.get("authority", "")),
            "key_id": str(value.get("key_id", "")),
            "artifact_digest": str(value.get("artifact_digest", "")),
            "control_plane_digest": str(value.get("control_plane_digest", "")),
            "policy_version": str(value.get("policy_version", "")),
            "issued_at": int(value.get("issued_at", 0)),
            "expires_at": int(value.get("expires_at", 0)),
            "nonce": str(value.get("nonce", "")),
            "signature": str(value.get("signature", "")),
        }
        if not all(fields[k] for k in fields if k not in {"issued_at", "expires_at"}):
            raise ExternalTrustError("incomplete external attestation")
        if fields["issued_at"] <= 0 or fields["expires_at"] <= fields["issued_at"]:
            raise ExternalTrustError("invalid attestation lifetime")
        return cls(**fields)

    def unsigned_payload(self) -> bytes:
        value = {
            "authority": self.authority,
            "key_id": self.key_id,
            "artifact_digest": self.artifact_digest,
            "control_plane_digest": self.control_plane_digest,
            "policy_version": self.policy_version,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
        }
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


class ExternalTrustVerifier:
    """Verifies attestations from an independent authorization authority."""

    MAX_LIFETIME_SECONDS = 900

    def __init__(self) -> None:
        pem = os.environ.get("CEUTIA_EXTERNAL_TRUST_PUBLIC_KEY", "")
        self.authority = os.environ.get("CEUTIA_EXTERNAL_TRUST_AUTHORITY", "")
        self.key_id = os.environ.get("CEUTIA_EXTERNAL_TRUST_KEY_ID", "")
        if not pem or not self.authority or not self.key_id:
            raise ExternalTrustError("external trust root is not configured")
        try:
            key = load_pem_public_key(pem.encode())
        except Exception as exc:  # fail closed on malformed configuration
            raise ExternalTrustError("invalid external trust public key") from exc
        if not isinstance(key, Ed25519PublicKey):
            raise ExternalTrustError("external trust key must be Ed25519")
        self._public_key = key

    @staticmethod
    def artifact_digest(artifact: bytes) -> str:
        return hashlib.sha256(artifact).hexdigest()

    def verify(
        self,
        attestation: ExternalAttestation,
        *,
        artifact_digest: str,
        control_plane_digest: str,
        policy_version: str,
        now: int | None = None,
    ) -> None:
        current = int(time.time()) if now is None else now
        if attestation.authority != self.authority:
            raise ExternalTrustError("untrusted authorization authority")
        if attestation.key_id != self.key_id:
            raise ExternalTrustError("unexpected authorization key")
        if attestation.artifact_digest != artifact_digest:
            raise ExternalTrustError("artifact attestation mismatch")
        if attestation.control_plane_digest != control_plane_digest:
            raise ExternalTrustError("control-plane attestation mismatch")
        if attestation.policy_version != policy_version:
            raise ExternalTrustError("policy-version attestation mismatch")
        if attestation.issued_at > current or current >= attestation.expires_at:
            raise ExternalTrustError("expired or not-yet-valid attestation")
        if attestation.expires_at - attestation.issued_at > self.MAX_LIFETIME_SECONDS:
            raise ExternalTrustError("attestation lifetime exceeds limit")
        if len(attestation.nonce) < 16:
            raise ExternalTrustError("attestation nonce is too short")
        try:
            signature = base64.b64decode(attestation.signature, validate=True)
            self._public_key.verify(signature, attestation.unsigned_payload())
        except (ValueError, InvalidSignature) as exc:
            raise ExternalTrustError("invalid external attestation signature") from exc
