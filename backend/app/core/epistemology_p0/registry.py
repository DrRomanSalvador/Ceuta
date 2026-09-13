"""
CeutIA - Registry de Claims y Evidencias (P0)

Ubicación aplanada: epistemology_p0/registry.py (no core/core).
Mantiene linaje completo. No resuelve contradicciones artificialmente.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid

from .epistemology.states import EpistemicStatus
from .evidence.models import Evidence, ContradictionLink, CorroborationLink, create_evidence
from .sources.independence import SourceIndependenceGraph
from .temporal.multitemporal import TemporalFilter


class ClaimRegistry:
    """Registro central de claims y evidencias asociadas."""

    def __init__(self, independence_graph: Optional[SourceIndependenceGraph] = None):
        self.claims: Dict[str, dict] = {}
        self.evidences: Dict[str, Evidence] = {}
        self.evidence_versions: Dict[str, List[Evidence]] = {}
        self.independence_graph = independence_graph or SourceIndependenceGraph()
        self.contradictions: List[ContradictionLink] = []

    def register_claim(
        self,
        statement: str,
        source_id: str,
        document_id: str,
        entities: Optional[List[str]] = None,
        claim_id: Optional[str] = None,
    ) -> str:
        cid = claim_id or f"claim-{uuid.uuid4().hex[:12]}"
        self.claims[cid] = {
            "claim_id": cid,
            "statement": statement,
            "source_id": source_id,
            "document_id": document_id,
            "entities": entities or [],
            "epistemic_status": EpistemicStatus.ATTRIBUTED_CLAIM.value,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "evidence_ids": [],
        }
        return cid

    def add_evidence(self, evidence: Evidence) -> str:
        eid = evidence.evidence_id
        self.evidences[eid] = evidence
        self.evidence_versions[eid] = [evidence]
        if evidence.claim_id in self.claims:
            self.claims[evidence.claim_id]["evidence_ids"].append(eid)
        return eid

    def add_evidence_version(self, new_version: Evidence) -> str:
        base_id = new_version.evidence_id
        if ":v" in base_id:
            base_id = base_id.split(":v")[0]
        if base_id not in self.evidence_versions:
            self.evidence_versions[base_id] = []
        self.evidence_versions[base_id].append(new_version)
        self.evidences[base_id] = new_version
        return new_version.evidence_id

    def register_contradiction(
        self,
        evidence_id_a: str,
        evidence_id_b: str,
        claim_id: str,
        divergence_reason: str,
        notes: Optional[str] = None,
    ) -> ContradictionLink:
        link = ContradictionLink(
            evidence_id=evidence_id_b,
            claim_id=claim_id,
            divergence_reason=divergence_reason,
            resolution_status="open",
            notes=notes,
        )
        self.contradictions.append(link)
        for eid in (evidence_id_a, evidence_id_b):
            if eid in self.evidences:
                old = self.evidences[eid]
                new_contras = list(old.contradictions) + [link]
                new_ev = old.create_new_version(
                    justification=f"Contradicción registrada: {divergence_reason}",
                    contradictions=new_contras,
                    epistemic_status=EpistemicStatus.CONTRADICTED,
                )
                self.add_evidence_version(new_ev)
        return link

    def corroborate(
        self,
        target_evidence_id: str,
        corroborating_evidence_id: str,
        independence_score: float,
        relationship_type: str,
        notes: Optional[str] = None,
    ) -> CorroborationLink:
        if target_evidence_id not in self.evidences:
            raise KeyError(f"Evidence {target_evidence_id} no encontrada")
        target = self.evidences[target_evidence_id]
        corr = self.evidences.get(corroborating_evidence_id)
        link = CorroborationLink(
            evidence_id=corroborating_evidence_id,
            source_id=corr.source_id if corr else "unknown",
            independence_score=independence_score,
            relationship_type=relationship_type,
            notes=notes,
        )
        new_corr_list = list(target.corroboration) + [link]
        new_status = target.epistemic_status
        if (
            independence_score >= 0.6
            and target.epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM
        ):
            new_status = EpistemicStatus.CORROBORATED_FACT
        new_ev = target.create_new_version(
            justification=(
                f"Corroboración con independencia={independence_score:.2f} "
                f"({relationship_type})"
            ),
            corroboration=new_corr_list,
            epistemic_status=new_status,
        )
        self.add_evidence_version(new_ev)
        return link

    def get_evidences_for_backtest(
        self,
        simulation_time: datetime,
        variable_filter: Optional[str] = None,
    ) -> List[Evidence]:
        all_ev = list(self.evidences.values())
        filtered = TemporalFilter.filter_by_ingestion_time(all_ev, simulation_time)
        TemporalFilter.assert_no_future_leak(filtered, simulation_time)
        return filtered

    def get_claim_lineage(self, claim_id: str) -> dict:
        if claim_id not in self.claims:
            raise KeyError(claim_id)
        claim = self.claims[claim_id]
        evs = [
            self.evidences[eid]
            for eid in claim["evidence_ids"]
            if eid in self.evidences
        ]
        return {
            "claim": claim,
            "evidences": [e.to_dict() for e in evs],
            "contradictions": [
                c.to_dict() if hasattr(c, "to_dict") else c
                for c in self.contradictions
                if c.claim_id == claim_id
            ],
        }
