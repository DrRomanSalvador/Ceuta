"""Non-invasive bridge between evidence selection and forecast incentives.

The bridge deliberately accepts identifiers rather than importing the primary
temporal/evidence implementation. This lets forecast reports carry an explicit
scientific provenance contract without competing with point-in-time evidence
work in the canonical runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .knowledge import EvidenceRequirement, ScientificKnowledgeRegistry


@dataclass(frozen=True, slots=True)
class ForecastEvidenceBinding:
    evidence_ids: tuple[str, ...]
    scientific_source_ids: tuple[str, ...]
    evidence_fingerprint: str
    requirement: EvidenceRequirement

    def __post_init__(self) -> None:
        if any(not value for value in self.evidence_ids + self.scientific_source_ids):
            raise ValueError("evidence identifiers must be non-empty")
        if not self.evidence_ids and not self.scientific_source_ids:
            raise ValueError("at least one evidence or scientific source identifier is required")
        if not self.evidence_fingerprint:
            raise ValueError("evidence_fingerprint is required")

    @property
    def provenance_hash(self) -> str:
        payload = {
            "evidence_ids": self.evidence_ids,
            "scientific_source_ids": self.scientific_source_ids,
            "evidence_fingerprint": self.evidence_fingerprint,
            "question_type": self.requirement.question_type,
            "domain": self.requirement.domain,
            "response_type": self.requirement.response_type,
            "minimum_evidence_level": self.requirement.minimum_evidence_level.value,
        }
        return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_binding(
    binding: ForecastEvidenceBinding,
    registry: ScientificKnowledgeRegistry,
) -> tuple[str, ...]:
    """Validate source identifiers and return the registry evidence trace.

    Runtime evidence IDs remain opaque to this layer; scientific source IDs are
    checked against the structured scientific registry. This preserves the
    separation between operational evidence records and bibliographic evidence.
    """
    for source_id in binding.scientific_source_ids:
        registry.get(source_id)
    response = registry.respond(binding.requirement)
    selected = set(response.source_ids)
    missing = [source_id for source_id in binding.scientific_source_ids if source_id not in selected]
    if missing:
        raise ValueError(f"scientific sources do not satisfy the declared evidence requirement: {missing}")
    return response.evidence_trace


__all__ = ["ForecastEvidenceBinding", "validate_binding"]
