"""Cross-cutting security, provenance, privacy and runtime integrity gates."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from string import hexdigits
from typing import Iterable, Sequence
from app.core.decision.control_plane import EvidenceDisposition, UncertaintyState
from .decision_lifecycle import DecisionEvidence
from ..evidence.source_registry import SourceRegistry, SourceRole, SourceVerification

@dataclass(frozen=True, slots=True)
class ProvenanceEnvelope:
    record_id:str; source_id:str; origin_id:str; content_hash:str; parent_hashes:tuple[str,...]=(); trust_score:float=1.0
@dataclass(frozen=True, slots=True)
class IntegrityAssessment:
    valid:bool; reasons:tuple[str,...]; chain_hash:str
@dataclass(frozen=True, slots=True)
class PrivacyPolicy:
    allowed_fields:frozenset[str]; minimum_aggregation_size:int=1; purpose:str="inference"

class IntegrityEngine:
    def verify(self,envelope:ProvenanceEnvelope,payload:bytes)->IntegrityAssessment:
        reasons=[]
        if envelope.content_hash != sha256(payload).hexdigest(): reasons.append("content hash mismatch")
        if not isfinite(envelope.trust_score) or not 0<=envelope.trust_score<=1: reasons.append("invalid trust score")
        if not envelope.record_id or not envelope.source_id or not envelope.origin_id: reasons.append("incomplete provenance")
        chain=sha256((envelope.record_id+envelope.content_hash+"|".join(envelope.parent_hashes)).encode()).hexdigest()
        return IntegrityAssessment(not reasons,tuple(reasons),chain)
    def enforce_policy(self,fields:Sequence[str],policy:PrivacyPolicy,population_size:int)->tuple[str,...]:
        if population_size<policy.minimum_aggregation_size: raise PermissionError("aggregation threshold not met")
        denied=tuple(sorted(set(fields)-policy.allowed_fields))
        if denied: raise PermissionError("fields outside privacy policy")
        return tuple(fields)

def validate_evidence_set(evidence:Sequence[DecisionEvidence], *, source_registry:SourceRegistry|None=None)->None:
    """Reject malformed evidence and, when available, require persisted verified sources."""
    seen:set[str]=set()
    for item in evidence:
        if item.evidence_id in seen: raise ValueError(f"duplicate evidence identity: {item.evidence_id}")
        seen.add(item.evidence_id)
        if not item.provenance_refs: raise ValueError(f"evidence lacks provenance: {item.evidence_id}")
        if len(item.content_hash)!=64 or any(char not in hexdigits for char in item.content_hash): raise ValueError(f"evidence content hash is not a valid SHA-256 hex digest: {item.evidence_id}")
        if item.assessment.evidence_id!=item.evidence_id or item.assessment.source_id!=item.source_id: raise ValueError(f"evidence assessment identity mismatch: {item.evidence_id}")
        if item.assessment.disposition in {EvidenceDisposition.BLOCK,EvidenceDisposition.QUARANTINE}: raise ValueError(f"blocked/quarantined evidence cannot be a decision input: {item.evidence_id}")
        if source_registry is not None:
            source=source_registry.source(item.source_id)
            if source is None: raise ValueError(f"evidence source is not registered: {item.source_id}")
            if source.role is not SourceRole.EVIDENCE: raise ValueError(f"decision evidence source has non-evidence role: {item.source_id}")
            if source.verification is SourceVerification.UNVERIFIED: raise ValueError(f"decision evidence source is unverified: {item.source_id}")

def validate_scenario_probabilities(probabilities:Sequence[float],tolerance:float=1e-6)->None:
    if not probabilities: raise ValueError("at least one scenario is required")
    if not isfinite(tolerance) or tolerance<0: raise ValueError("probability tolerance must be finite and non-negative")
    if any(not isfinite(p) or p<0 or p>1 for p in probabilities): raise ValueError("scenario probabilities must be finite values in [0,1]")
    total=sum(probabilities)
    if not isfinite(total) or abs(total-1.0)>tolerance: raise ValueError(f"scenario probabilities must sum to 1; got {total}")

def propagate_uncertainty(states:Iterable[UncertaintyState],*,method:str="conservative-max")->UncertaintyState:
    items=tuple(states)
    if not items: return UncertaintyState(1.0,source_refs=(),method=method)
    value=sum(x.value for x in items)/len(items) if method=="mean" else max(x.value for x in items)
    return UncertaintyState(value,source_refs=tuple(ref for state in items for ref in state.source_refs),method=method)
__all__=["IntegrityAssessment","IntegrityEngine","PrivacyPolicy","ProvenanceEnvelope","propagate_uncertainty","validate_evidence_set","validate_scenario_probabilities"]
