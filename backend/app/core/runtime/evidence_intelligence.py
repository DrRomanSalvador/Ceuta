"""Evidence synthesis that distinguishes source count from independent evidence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    source_id: str
    origin_id: str
    reliability: float
    epistemic_status: str
    supports: tuple[str,...]=()
    contradicts: tuple[str,...]=()

@dataclass(frozen=True, slots=True)
class EvidenceSynthesis:
    evidence_ids: tuple[str,...]
    independent_origins: tuple[str,...]
    effective_independent_count: float
    support_ids: tuple[str,...]
    contradiction_ids: tuple[str,...]

class EvidenceIntelligence:
    def synthesize(self, evidence: Sequence[EvidenceItem]) -> EvidenceSynthesis:
        origins={e.origin_id for e in evidence}
        by_origin={origin: max((e.reliability for e in evidence if e.origin_id==origin),default=0.0) for origin in origins}
        support=tuple(e.evidence_id for e in evidence if e.supports)
        contradiction=tuple(e.evidence_id for e in evidence if e.contradicts)
        effective=sum(by_origin.values())
        return EvidenceSynthesis(tuple(e.evidence_id for e in evidence),tuple(sorted(origins)),effective,support,contradiction)
