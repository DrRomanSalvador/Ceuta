"""
CeutIA ↔ Serpiente - Contrato de datos versionado

CeutIA NUNCA entrega escalares desnudos.
Toda observación conserva: significado, procedencia, incertidumbre,
temporalidad y estado epistemológico.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import uuid

SCHEMA_VERSION = "1.0"


@dataclass
class SourceRef:
    source_id: str
    document_id: str
    claim_id: str


@dataclass
class TimeBlock:
    event_start: Optional[str] = None
    event_end: Optional[str] = None
    publication_time: Optional[str] = None
    ingestion_time: Optional[str] = None
    revision_time: Optional[str] = None
    detection_time: Optional[str] = None
    assessment_time: Optional[str] = None
    impact_time: Optional[str] = None


@dataclass
class UncertaintyBlock:
    type: str = "interval"
    lower: Optional[float] = None
    upper: Optional[float] = None
    value: Optional[float] = None


@dataclass
class ProvenanceOp:
    operation: str
    rule: str
    actor: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class Observation:
    """Observación estructurada que CeutIA entrega a Serpiente."""
    variable: str
    value: Any
    unit: Optional[str]
    semantic_definition: str
    time: TimeBlock
    geography: Optional[str]
    source: SourceRef
    provenance: List[ProvenanceOp]
    confidence: float
    uncertainty: Optional[UncertaintyBlock]
    source_dependence_ratio: float
    corroboration: List[dict]
    contradictions: List[dict]
    methodology: Optional[str]
    epistemic_status: str
    schema_version: str = SCHEMA_VERSION
    observation_id: str = field(default_factory=lambda: f"obs-{uuid.uuid4().hex[:12]}")
    emitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "observation_id": self.observation_id,
            "variable": self.variable,
            "value": self.value,
            "unit": self.unit,
            "semantic_definition": self.semantic_definition,
            "time": asdict(self.time),
            "geography": self.geography,
            "source": asdict(self.source),
            "provenance": [asdict(p) for p in self.provenance],
            "confidence": self.confidence,
            "uncertainty": asdict(self.uncertainty) if self.uncertainty else None,
            "source_dependence_ratio": self.source_dependence_ratio,
            "corroboration": self.corroboration,
            "contradictions": self.contradictions,
            "methodology": self.methodology,
            "epistemic_status": self.epistemic_status,
            "schema_version": self.schema_version,
            "emitted_at": self.emitted_at,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class PullContextRequest:
    variable: str
    interval_start: str
    interval_end: str
    geography: Optional[str]
    anomaly_type: str
    competing_hypotheses: List[str] = field(default_factory=list)
    request_id: str = field(default_factory=lambda: f"ctx-{uuid.uuid4().hex[:12]}")
    requested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContextExplanation:
    explanation_type: str
    description: str
    supporting_evidence_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5
    epistemic_status: str = "HYPOTHESIS"


@dataclass
class ContextDossier:
    request_id: str
    variable: str
    explanations: List[ContextExplanation]
    rival_hypotheses: List[str]
    related_evidence_ids: List[str]
    notes: Optional[str] = None
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "variable": self.variable,
            "explanations": [asdict(e) for e in self.explanations],
            "rival_hypotheses": self.rival_hypotheses,
            "related_evidence_ids": self.related_evidence_ids,
            "notes": self.notes,
            "generated_at": self.generated_at,
            "schema_version": self.schema_version,
        }
