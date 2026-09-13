"""Operational provenance gate linking scientific evidence to registered sources and citations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from .citation_trace import CitationTraceRegistry
from .source_registry import SourceRegistry, SourceRole, SourceVerification


class ProvenanceDisposition(StrEnum):
    ALLOW = "allow"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class ProvenanceGateResult:
    disposition: ProvenanceDisposition
    reasons: tuple[str, ...]


class EvidenceProvenanceGate:
    """Prevents evidence from entering a decision path without registered provenance."""

    def __init__(self, registry: SourceRegistry, citations: CitationTraceRegistry | None = None) -> None:
        self.registry = registry
        self.citations = citations

    def evaluate(self, evidence_ids: Sequence[str], *, claim_ids: Sequence[str] = (), high_impact: bool = False) -> ProvenanceGateResult:
        reasons: list[str] = []
        for evidence_id in evidence_ids:
            source = self.registry.source(evidence_id)
            if source is None:
                reasons.append(f"{evidence_id}:source_not_registered")
                continue
            if source.role is not SourceRole.EVIDENCE:
                reasons.append(f"{evidence_id}:source_role_not_evidence")
            if source.verification is SourceVerification.UNVERIFIED:
                reasons.append(f"{evidence_id}:source_not_verified")
        if claim_ids:
            for claim_id in claim_ids:
                if not self.registry.evidence_traceable(claim_id):
                    reasons.append(f"{claim_id}:claim_not_traceable")
                if high_impact and self.citations is not None and not self.citations.traceable(claim_id):
                    reasons.append(f"{claim_id}:exact_citation_missing")
        if any(reason.endswith("source_not_registered") for reason in reasons):
            return ProvenanceGateResult(ProvenanceDisposition.ABSTAIN, tuple(reasons))
        if reasons:
            return ProvenanceGateResult(ProvenanceDisposition.HUMAN_REVIEW, tuple(reasons))
        return ProvenanceGateResult(ProvenanceDisposition.ALLOW, ())


__all__ = ["EvidenceProvenanceGate", "ProvenanceDisposition", "ProvenanceGateResult"]
