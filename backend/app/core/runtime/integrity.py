"""Security, provenance, privacy and integrity gates for live inference."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

@dataclass(frozen=True, slots=True)
class ProvenanceEnvelope:
    record_id: str
    source_id: str
    origin_id: str
    content_hash: str
    parent_hashes: tuple[str,...]=()
    trust_score: float=1.0

@dataclass(frozen=True, slots=True)
class IntegrityAssessment:
    valid: bool
    reasons: tuple[str,...]
    chain_hash: str

@dataclass(frozen=True, slots=True)
class PrivacyPolicy:
    allowed_fields: frozenset[str]
    minimum_aggregation_size: int=1
    purpose: str="inference"

class IntegrityEngine:
    def verify(self, envelope: ProvenanceEnvelope, payload: bytes) -> IntegrityAssessment:
        reasons=[]
        if envelope.content_hash != sha256(payload).hexdigest(): reasons.append("content hash mismatch")
        if not 0 <= envelope.trust_score <= 1: reasons.append("invalid trust score")
        if not envelope.record_id or not envelope.source_id or not envelope.origin_id: reasons.append("incomplete provenance")
        chain=sha256((envelope.record_id+envelope.content_hash+"|".join(envelope.parent_hashes)).encode()).hexdigest()
        return IntegrityAssessment(not reasons,tuple(reasons),chain)

    def enforce_policy(self, fields: Sequence[str], policy: PrivacyPolicy, population_size: int) -> tuple[str,...]:
        if population_size < policy.minimum_aggregation_size: raise PermissionError("aggregation threshold not met")
        denied=tuple(sorted(set(fields)-policy.allowed_fields))
        if denied: raise PermissionError("fields outside privacy policy")
        return tuple(fields)
