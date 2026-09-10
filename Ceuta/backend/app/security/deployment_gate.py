"""Fail-closed deployment admission using an external trust attestation."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .external_trust import ExternalAttestation, ExternalTrustError, ExternalTrustVerifier


class DeploymentAdmissionError(RuntimeError):
    """Raised when an artifact is not independently authorized to execute."""


def protected_control_plane_digest(root: Path) -> str:
    """Hash protected control-plane files deterministically."""
    names = [
        "SUPREME_SECURITY_LAW.md",
        "OWNER_AUTHORITY_ROOT.md",
        "OWNER_SECURITY_AND_LIABILITY_CONTROL_PLANE.md",
        "HUMAN_RIGHTS_MEDICAL_LEGAL_NATIONAL_SECURITY_AND_DUAL_USE_CONTROL.md",
        "AI_AUTONOMY_BOUNDARY.md",
        "OWNER_COMPROMISE_RECOVERY_PROTOCOL.md",
        "SECURITY_EXTREME_CONTROL_MATRIX.md",
        "SECURITY_TECHNICAL_ENFORCEMENT_ARCHITECTURE.md",
        "SECURITY_RUNTIME_ENFORCEMENT.md",
        "AGENTS.md",
        "AI_MANDATORY_SYSTEM_CONSTITUTION.md",
        "SUPRMIND_AI_COUNCIL_CONSTITUTION.md",
        "AI_SECURITY_INCIDENT_LESSONS.md",
        "AI_SECURITY_INCIDENT_LESSONS_EXTENDED.md",
        ".github/CODEOWNERS",
        ".github/workflows/security-control-plane.yml",
    ]
    digest = hashlib.sha256()
    for name in names:
        path = root / name
        if not path.is_file():
            raise DeploymentAdmissionError(f"missing protected control: {name}")
        data = path.read_bytes()
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def admit_current_artifact(repo_root: Path, artifact: bytes, attestation_json: dict) -> None:
    """Admit execution only when an external authority attests exact state."""
    try:
        verifier = ExternalTrustVerifier()
        attestation = ExternalAttestation.from_dict(attestation_json)
        artifact_digest = verifier.artifact_digest(artifact)
        control_digest = protected_control_plane_digest(repo_root)
        policy_version = os.environ.get("CEUTIA_POLICY_VERSION", "")
        if not policy_version:
            raise DeploymentAdmissionError("policy version is not configured")
        verifier.verify(
            attestation,
            artifact_digest=artifact_digest,
            control_plane_digest=control_digest,
            policy_version=policy_version,
        )
    except (ExternalTrustError, OSError, ValueError) as exc:
        raise DeploymentAdmissionError("external deployment admission failed closed") from exc
