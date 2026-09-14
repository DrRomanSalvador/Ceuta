"""
CeutIA - Registry de Claims y Evidencias (P0)

Mantiene linaje completo. No resuelve contradicciones artificialmente y no
permite que una única relación de corroboración produzca un hecho corroborado.
"""

from __future__ import annotations

from datetime import UTC, datetime
import uuid
from typing import Dict, List, Optional

from .epistemology.states import EpistemicStatus
from .evidence.models import CorroborationLink, ContradictionLink, Evidence, UncertaintyType
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

    def register_claim(self, statement: str, source_id: str, document_id: str, entities: Optional[List[str]] = None, claim_id: Optional[str] = None) -> str:
        cid = claim_id or f"claim-{uuid.uuid4().hex[:12]}"
        self.claims[cid] = {
            "claim_id": cid,
            "statement": statement,
            "source_id": source_id,
            "document_id": document_id,
            "entities": entities or [],
            "epistemic_status": EpistemicStatus.ATTRIBUTED_CLAIM.value,
            "registered_at": datetime.now(UTC).isoformat(),
            "evidence_ids": [],
        }
        return cid

    def add_evidence(self, evidence: Evidence) -> str:
        """Admit legacy evidence only after canonical P0 contract validation."""
        self._validate_p0_contract(evidence)
        eid = evidence.evidence_id
        self.evidences[eid] = evidence
        self.evidence_versions.setdefault(eid, []).append(evidence)
        if evidence.claim_id in self.claims:
            self.claims[evidence.claim_id]["evidence_ids"].append(eid)
        return eid

    def _validate_p0_contract(self, evidence: Evidence) -> object:
        """Normalize legacy Evidence into the canonical contract without upgrading it."""
        from ..p0_contracts import EvidenceContract, ProvenanceLink, SourceRelation
        from ..p0_contracts import Uncertainty as P0Uncertainty

        relation = self._source_relation(evidence.source_independence, SourceRelation)
        uncertainty = self._uncertainty_contract(evidence, P0Uncertainty)
        independent_ids = {evidence.source_id if relation is SourceRelation.INDEPENDENT else None}
        corroborating_ids: list[str] = []
        for link in evidence.corroboration:
            if link.relationship_type.strip().upper() == SourceRelation.INDEPENDENT.value and link.independence_score >= 0.6:
                independent_ids.add(link.source_id)
                corroborating_ids.append(link.evidence_id)
        independent_ids.discard(None)

        publication = evidence.publication_time
        revision = evidence.revision_time
        ingestion = evidence.ingestion_time
        claim = self.claims.get(evidence.claim_id, {}).get("statement", evidence.semantic_definition)
        return EvidenceContract(
            evidence_id=evidence.evidence_id,
            claim=str(claim),
            source_id=evidence.source_id,
            publication_time=publication,
            event_time=evidence.event_time,
            observed_at=publication or evidence.ingestion_time,
            ingestion_time=ingestion,
            revision_time=revision,
            uncertainty=uncertainty,
            epistemic_status=evidence.epistemic_status,
            source_relation=relation,
            provenance=(ProvenanceLink(
                source_id=evidence.source_id,
                source_version=f"v{evidence.version}",
                relation=relation,
                transformation="legacy-evidence-to-p0-contract",
            ),),
            corroborating_evidence_ids=tuple(dict.fromkeys(corroborating_ids)),
            independent_source_count=len(independent_ids),
            limitations=tuple([
                "Legacy Evidence normalized through the canonical P0 contract.",
                *evidence.unavailable_fields.values(),
            ]),
        )

    @staticmethod
    def _source_relation(value: str, source_relation: object) -> object:
        normalized = value.strip().upper()
        try:
            return source_relation(normalized)
        except ValueError:
            return source_relation.UNKNOWN

    @staticmethod
    def _uncertainty_contract(evidence: Evidence, uncertainty_type: type) -> object:
        from ..p0_contracts import Uncertainty as P0Uncertainty
        if evidence.uncertainty is None or evidence.uncertainty.type is UncertaintyType.UNKNOWN:
            return P0Uncertainty(kind="unknown", description="uncertainty not quantified by legacy source")
        return P0Uncertainty(
            kind=evidence.uncertainty.type.value,
            lower=evidence.uncertainty.lower,
            upper=evidence.uncertainty.upper,
            description=evidence.uncertainty.qualitative or "uncertainty represented by legacy evidence contract",
        )

    def add_evidence_version(self, new_version: Evidence) -> str:
        base_id = new_version.evidence_id.split(":v")[0]
        self.evidence_versions.setdefault(base_id, [])
        self._validate_p0_contract(new_version)
        self.evidence_versions[base_id].append(new_version)
        self.evidences[base_id] = new_version
        return new_version.evidence_id

    def register_contradiction(self, evidence_id_a: str, evidence_id_b: str, claim_id: str, divergence_reason: str, notes: Optional[str] = None) -> ContradictionLink:
        link = ContradictionLink(evidence_id=evidence_id_b, claim_id=claim_id, divergence_reason=divergence_reason, resolution_status="open", notes=notes)
        self.contradictions.append(link)
        for eid in (evidence_id_a, evidence_id_b):
            if eid in self.evidences:
                old = self.evidences[eid]
                new_ev = old.create_new_version(
                    justification=f"Contradicción registrada: {divergence_reason}",
                    contradictions=list(old.contradictions) + [link],
                    epistemic_status=EpistemicStatus.CONTRADICTED,
                )
                self.add_evidence_version(new_ev)
        return link

    def corroborate(self, target_evidence_id: str, corroborating_evidence_id: str, independence_score: float, relationship_type: str, notes: Optional[str] = None) -> CorroborationLink:
        if target_evidence_id not in self.evidences:
            raise KeyError(f"Evidence {target_evidence_id} no encontrada")
        corr = self.evidences.get(corroborating_evidence_id)
        if corr is None:
            raise KeyError(f"Evidence {corroborating_evidence_id} no encontrada")
        if not 0.0 <= independence_score <= 1.0:
            raise ValueError("independence_score must be between 0 and 1")
        link = CorroborationLink(evidence_id=corroborating_evidence_id, source_id=corr.source_id, independence_score=independence_score, relationship_type=relationship_type, notes=notes)
        target = self.evidences[target_evidence_id]
        new_corr_list = list(target.corroboration) + [link]
        independent_sources = {target.source_id if target.source_independence.strip().lower() == "independent" else None}
        for existing in new_corr_list:
            if existing.relationship_type.strip().upper() == "INDEPENDENT" and existing.independence_score >= 0.6:
                independent_sources.add(existing.source_id)
        independent_sources.discard(None)
        new_status = target.epistemic_status
        if target.epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM and len(independent_sources) >= 2:
            new_status = EpistemicStatus.CORROBORATED_FACT
        new_ev = target.create_new_version(
            justification=(f"Corroboración registrada: relationship={relationship_type}, independence={independence_score:.2f}; independent_source_count={len(independent_sources)}"),
            corroboration=new_corr_list,
            epistemic_status=new_status,
        )
        self.add_evidence_version(new_ev)
        return link

    def get_evidences_for_backtest(self, simulation_time: datetime, variable_filter: Optional[str] = None) -> List[Evidence]:
        all_versions = [
            evidence
            for versions in self.evidence_versions.values()
            for evidence in versions
        ]
        if not all_versions:
            all_versions = list(self.evidences.values())
        filtered = TemporalFilter.snapshot_by_available_at(all_versions, simulation_time)
        TemporalFilter.assert_no_future_leak(filtered, simulation_time)
        if variable_filter is None:
            return filtered
        return [ev for ev in filtered if getattr(ev, "variable", None) == variable_filter or ev.to_dict().get("variable") == variable_filter or ev.semantic_definition == variable_filter]

    def get_claim_lineage(self, claim_id: str) -> dict:
        if claim_id not in self.claims:
            raise KeyError(claim_id)
        claim = self.claims[claim_id]
        evs = [self.evidences[eid] for eid in claim["evidence_ids"] if eid in self.evidences]
        return {
            "claim": claim,
            "evidences": [e.to_dict() for e in evs],
            "contradictions": [c.to_dict() if hasattr(c, "to_dict") else c for c in self.contradictions if c.claim_id == claim_id],
        }
