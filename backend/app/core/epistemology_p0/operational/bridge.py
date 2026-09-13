"""
P1 — Bridge CeutIA → salida contractual (hacia Serpiente u otros consumidores).

Garantiza que ninguna observación pierda significado, procedencia,
incertidumbre, temporalidad ni estado epistemológico.
"""

from __future__ import annotations
from typing import Optional, Any
from datetime import datetime, timezone

from ..evidence.models import Evidence
from ..contracts.ceutia_serpiente import (
    Observation,
    SourceRef,
    TimeBlock,
    UncertaintyBlock,
    ProvenanceOp,
)
from .uncertainty import weight_by_confidence, IntervalUncertainty


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def emit_observation_from_evidence(
    evidence: Evidence,
    *,
    variable: str,
    geography: Optional[str] = None,
) -> Observation:
    """Convierte Evidence (P0) en Observation contractual (P1)."""
    unc = None
    if evidence.uncertainty is not None:
        unc = UncertaintyBlock(
            type=evidence.uncertainty.type.value
            if hasattr(evidence.uncertainty.type, "value")
            else str(evidence.uncertainty.type),
            lower=evidence.uncertainty.lower,
            upper=evidence.uncertainty.upper,
            value=evidence.uncertainty.value,
        )

    prov = [
        ProvenanceOp(
            operation=p.operation,
            rule=p.rule,
            actor=getattr(p, "actor", None),
            timestamp=p.timestamp.isoformat() if getattr(p, "timestamp", None) else None,
        )
        for p in (evidence.provenance or [])
    ]

    dep_ratio = 0.0
    if evidence.corroboration:
        scores = [1.0 - c.independence_score for c in evidence.corroboration]
        dep_ratio = sum(scores) / len(scores)

    geo = geography
    if geo is None and evidence.location is not None:
        geo = evidence.location.value

    return Observation(
        variable=variable,
        value=evidence.value,
        unit=evidence.unit,
        semantic_definition=evidence.semantic_definition,
        time=TimeBlock(
            event_start=_iso(evidence.event_time),
            publication_time=_iso(evidence.publication_time),
            ingestion_time=_iso(evidence.ingestion_time),
            revision_time=_iso(evidence.revision_time),
            detection_time=_iso(evidence.detection_time),
            assessment_time=_iso(evidence.assessment_time),
            impact_time=_iso(evidence.impact_time),
        ),
        geography=geo,
        source=SourceRef(
            source_id=evidence.source_id,
            document_id=evidence.document_id,
            claim_id=evidence.claim_id,
        ),
        provenance=prov,
        confidence=evidence.source_reliability,
        uncertainty=unc,
        source_dependence_ratio=round(dep_ratio, 4),
        corroboration=[c.to_dict() for c in evidence.corroboration],
        contradictions=[c.to_dict() for c in evidence.contradictions],
        methodology=evidence.methodology,
        epistemic_status=evidence.epistemic_status.value
        if hasattr(evidence.epistemic_status, "value")
        else str(evidence.epistemic_status),
    )


class ObservationBridge:
    """Puente operativo: Evidence/Registry → Observation + peso para modelos."""

    def emit(self, evidence: Evidence, variable: str, geography: Optional[str] = None) -> Observation:
        return emit_observation_from_evidence(evidence, variable=variable, geography=geography)

    def model_weight(self, observation: Observation) -> float:
        """Peso que un consumidor (Serpiente) debería usar."""
        return weight_by_confidence(
            observation.confidence,
            observation.source_dependence_ratio,
        )

    def as_payload(self, observation: Observation) -> dict:
        payload = observation.to_dict()
        payload["model_weight"] = self.model_weight(observation)
        return payload
