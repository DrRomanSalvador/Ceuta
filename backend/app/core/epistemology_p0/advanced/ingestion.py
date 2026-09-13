"""
P2 — Ingesta masiva estructurada.

Cada registro debe declarar suficiente temporalidad para establecer cuándo la
información pudo entrar en análisis. No se usa event_time como disponibilidad.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterable
from datetime import datetime, timezone
import uuid

from app.core.p0_contracts import EvidenceContract, SourceRelation, Uncertainty as ContractUncertainty
from ..evidence.models import create_evidence, Evidence, Location, UncertaintyType, ProvenanceStep
from ..epistemology.states import EpistemicStatus
from ..registry import ClaimRegistry
from .semantic_graph import SemanticGraph


@dataclass
class IngestionRecord:
    source_id: str
    document_id: str
    statement: str
    value: Any
    semantic_definition: str
    source_reliability: float = 0.5
    source_independence: str = "unknown"
    unit: Optional[str] = None
    variable: Optional[str] = None
    geography: Optional[str] = None
    event_time: Optional[str] = None
    publication_time: Optional[str] = None
    methodology: Optional[str] = None
    unavailable_fields: Dict[str, str] = field(default_factory=dict)
    external_id: Optional[str] = None


@dataclass
class IngestionBatch:
    batch_id: str
    records: List[IngestionRecord]
    actor: str = "ingestion_pipeline"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class IngestionResult:
    batch_id: str
    accepted: int
    rejected: int
    claim_ids: List[str]
    evidence_ids: List[str]
    errors: List[dict]
    duration_ms: float

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "claim_ids": self.claim_ids,
            "evidence_ids": self.evidence_ids,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
        }


class BulkIngestionPipeline:
    """Ingesta por lotes hacia ClaimRegistry + SemanticGraph."""

    def __init__(self, registry: ClaimRegistry, graph: Optional[SemanticGraph] = None):
        self.registry = registry
        self.graph = graph or SemanticGraph()

    def ingest_batch(self, batch: IngestionBatch) -> IngestionResult:
        t0 = datetime.now(timezone.utc)
        accepted = 0
        rejected = 0
        claim_ids: List[str] = []
        evidence_ids: List[str] = []
        errors: List[dict] = []

        for i, rec in enumerate(batch.records):
            try:
                self._validate(rec)
                cid = self.registry.register_claim(
                    statement=rec.statement,
                    source_id=rec.source_id,
                    document_id=rec.document_id,
                )
                loc = Location(type="region", value=rec.geography) if rec.geography else None

                event_time = self._parse_dt(rec.event_time)
                publication_time = self._parse_dt(rec.publication_time)
                unavailable = dict(rec.unavailable_fields)
                if event_time is None and "event_time" not in unavailable:
                    unavailable["event_time"] = "not_provided_in_batch"

                now = datetime.now(timezone.utc)
                # Without a trustworthy publication/observation timestamp, the
                # first system observation is the conservative availability bound.
                observed_at = publication_time or now
                relation = self._source_relation(rec.source_independence)
                provenance = [
                    ProvenanceStep(
                        operation="ingest",
                        rule="P0 observation boundary admission",
                        actor=batch.actor,
                        timestamp=now,
                        input_refs=(rec.external_id,) if rec.external_id else (),
                    )
                ]

                ev = create_evidence(
                    source_id=rec.source_id,
                    document_id=rec.document_id,
                    claim_id=cid,
                    value=rec.value,
                    unit=rec.unit,
                    semantic_definition=rec.semantic_definition,
                    source_reliability=rec.source_reliability,
                    source_independence=rec.source_independence,
                    location=loc,
                    event_time=event_time,
                    publication_time=publication_time,
                    methodology=rec.methodology,
                    provenance=provenance,
                    unavailable_fields=unavailable,
                    epistemic_status=EpistemicStatus.ATTRIBUTED_CLAIM,
                )
                # Validate the exact representation before registry/graph admission.
                self._validate_contract(
                    ev,
                    claim=rec.statement,
                    observed_at=observed_at,
                    source_relation=relation,
                )
                eid = self.registry.add_evidence(ev)
                claim_ids.append(cid)
                evidence_ids.append(eid)

                self.graph.link_evidence_chain(
                    source_id=rec.source_id,
                    source_label=rec.source_id,
                    document_id=rec.document_id,
                    document_label=rec.document_id,
                    claim_id=cid,
                    claim_label=rec.statement[:120],
                    evidence_id=eid,
                    evidence_label=f"{rec.variable or 'value'}={rec.value}",
                    variable=rec.variable,
                )
                accepted += 1
            except Exception as exc:
                rejected += 1
                errors.append({"index": i, "external_id": rec.external_id, "error": str(exc)})

        t1 = datetime.now(timezone.utc)
        return IngestionResult(
            batch_id=batch.batch_id,
            accepted=accepted,
            rejected=rejected,
            claim_ids=claim_ids,
            evidence_ids=evidence_ids,
            errors=errors,
            duration_ms=round((t1 - t0).total_seconds() * 1000.0, 3),
        )

    def ingest_records(self, records: Iterable[IngestionRecord], *, actor: str = "ingestion_pipeline") -> IngestionResult:
        return self.ingest_batch(
            IngestionBatch(
                batch_id=f"batch-{uuid.uuid4().hex[:12]}",
                records=list(records),
                actor=actor,
            )
        )

    @staticmethod
    def _validate(rec: IngestionRecord) -> None:
        if not rec.source_id or not rec.document_id:
            raise ValueError("source_id and document_id required")
        if not rec.semantic_definition or not rec.semantic_definition.strip():
            raise ValueError("semantic_definition required")
        if not 0.0 <= rec.source_reliability <= 1.0:
            raise ValueError("source_reliability out of range")

    @staticmethod
    def _parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"invalid temporal value: {value!r}") from exc
        if parsed.tzinfo is None:
            raise ValueError("temporal values must be timezone-aware")
        return parsed

    @staticmethod
    def _source_relation(value: str) -> SourceRelation:
        normalized = value.strip().lower()
        mapping = {
            "independent": SourceRelation.INDEPENDENT,
            "primary": SourceRelation.INDEPENDENT,
            "dependent": SourceRelation.DEPENDENT,
            "copy": SourceRelation.COPY,
            "amplifier": SourceRelation.AMPLIFIER,
            "unknown": SourceRelation.UNKNOWN,
        }
        return mapping.get(normalized, SourceRelation.UNKNOWN)

    @staticmethod
    def _validate_contract(
        evidence: Evidence,
        *,
        claim: str,
        observed_at: datetime,
        source_relation: SourceRelation,
    ) -> EvidenceContract:
        uncertainty = evidence.uncertainty
        assert uncertainty is not None
        return EvidenceContract(
            evidence_id=evidence.evidence_id,
            claim=claim,
            source_id=evidence.source_id,
            publication_time=evidence.publication_time,
            event_time=evidence.event_time,
            observed_at=observed_at,
            ingestion_time=evidence.ingestion_time,
            revision_time=evidence.revision_time,
            uncertainty=ContractUncertainty(
                kind=uncertainty.type.value,
                lower=uncertainty.lower,
                upper=uncertainty.upper,
                description=uncertainty.qualitative or "uncertainty not quantified by source",
            ),
            epistemic_status=evidence.epistemic_status,
            source_relation=source_relation,
            limitations=tuple(
                f"unavailable:{key}={value}" for key, value in evidence.unavailable_fields.items()
            ),
        )
