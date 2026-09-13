"""
CeutIA - Objeto de Evidencia Versionado e Inmutable (P0)

Cada evidencia es inmutable una vez registrada.
Correcciones o ampliaciones = nuevas versiones.
Linaje completo desde el dato bruto.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from enum import Enum
import uuid

from ..epistemology.states import EpistemicStatus


class UncertaintyType(str, Enum):
    INTERVAL = "interval"
    STANDARD_DEVIATION = "standard_deviation"
    CONFIDENCE_INTERVAL = "confidence_interval"
    QUALITATIVE = "qualitative"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Uncertainty:
    type: UncertaintyType
    lower: Optional[float] = None
    upper: Optional[float] = None
    value: Optional[float] = None
    qualitative: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"type": self.type.value}
        if self.lower is not None:
            d["lower"] = self.lower
        if self.upper is not None:
            d["upper"] = self.upper
        if self.value is not None:
            d["value"] = self.value
        if self.qualitative is not None:
            d["qualitative"] = self.qualitative
        return d


@dataclass(frozen=True)
class Location:
    type: str
    value: str
    resolution: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        d = {"type": self.type, "value": self.value}
        if self.resolution:
            d["resolution"] = self.resolution
        if self.notes:
            d["notes"] = self.notes
        return d


@dataclass(frozen=True)
class ProvenanceStep:
    operation: str
    rule: str
    actor: str
    timestamp: datetime
    input_refs: Tuple[str, ...] = ()
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "rule": self.rule,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
            "input_refs": list(self.input_refs),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class CorroborationLink:
    evidence_id: str
    source_id: str
    independence_score: float
    relationship_type: str
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "independence_score": self.independence_score,
            "relationship_type": self.relationship_type,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ContradictionLink:
    evidence_id: str
    claim_id: str
    divergence_reason: str
    resolution_status: str
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "claim_id": self.claim_id,
            "divergence_reason": self.divergence_reason,
            "resolution_status": self.resolution_status,
            "notes": self.notes,
        }


@dataclass
class Evidence:
    """Evidencia versionada e inmutable. Correcciones = nueva versión."""

    evidence_id: str
    version: int
    source_id: str
    document_id: str
    claim_id: str
    event_id: Optional[str]
    value: Any
    unit: Optional[str]
    semantic_definition: str
    location: Optional[Location]
    event_time: Optional[datetime]
    publication_time: Optional[datetime]
    ingestion_time: datetime
    revision_time: Optional[datetime]
    detection_time: Optional[datetime]
    assessment_time: Optional[datetime]
    impact_time: Optional[datetime]
    methodology: Optional[str]
    source_reliability: float
    source_independence: str
    uncertainty: Optional[Uncertainty]
    provenance: List[ProvenanceStep]
    transformation_history: List[dict]
    corroboration: List[CorroborationLink]
    contradictions: List[ContradictionLink]
    epistemic_status: EpistemicStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_immutable: bool = True
    parent_version_id: Optional[str] = None
    unavailable_fields: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.semantic_definition or not self.semantic_definition.strip():
            raise ValueError("semantic_definition es obligatorio")
        if not 0.0 <= self.source_reliability <= 1.0:
            raise ValueError("source_reliability debe estar entre 0.0 y 1.0")
        if self.ingestion_time is None:
            raise ValueError("ingestion_time es obligatorio")
        if self.ingestion_time.tzinfo is None:
            raise ValueError("ingestion_time debe ser timezone-aware")
        for name in (
            "event_time", "publication_time", "revision_time", "detection_time",
            "assessment_time", "impact_time", "created_at",
        ):
            value = getattr(self, name)
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} debe ser timezone-aware")

    @property
    def available_at(self) -> datetime:
        """Single legacy-compatible analytical availability boundary.

        Event time is deliberately excluded. A revised version becomes available
        at its revision time; otherwise publication time is preferred, and the
        ingestion timestamp is the conservative lower-information fallback.
        """
        return self.revision_time or self.publication_time or self.ingestion_time

    def to_dict(self) -> dict:
        def _ser(obj: Any) -> Any:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            if isinstance(obj, list):
                return [_ser(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _ser(v) for k, v in obj.items()}
            return obj

        return {
            "evidence_id": self.evidence_id,
            "version": self.version,
            "source_id": self.source_id,
            "document_id": self.document_id,
            "claim_id": self.claim_id,
            "event_id": self.event_id,
            "value": self.value,
            "unit": self.unit,
            "semantic_definition": self.semantic_definition,
            "location": _ser(self.location) if self.location else None,
            "event_time": _ser(self.event_time),
            "publication_time": _ser(self.publication_time),
            "available_at": _ser(self.available_at),
            "ingestion_time": _ser(self.ingestion_time),
            "revision_time": _ser(self.revision_time),
            "detection_time": _ser(self.detection_time),
            "assessment_time": _ser(self.assessment_time),
            "impact_time": _ser(self.impact_time),
            "methodology": self.methodology,
            "source_reliability": self.source_reliability,
            "source_independence": self.source_independence,
            "uncertainty": _ser(self.uncertainty) if self.uncertainty else None,
            "provenance": _ser(self.provenance),
            "transformation_history": self.transformation_history,
            "corroboration": _ser(self.corroboration),
            "contradictions": _ser(self.contradictions),
            "epistemic_status": self.epistemic_status.value,
            "created_at": _ser(self.created_at),
            "parent_version_id": self.parent_version_id,
            "unavailable_fields": self.unavailable_fields,
            "schema_version": "1.0",
        }

    def create_new_version(self, justification: str, actor: str = "system", **updates: Any) -> "Evidence":
        if not justification or not justification.strip():
            raise ValueError("Toda nueva versión requiere justificación")

        new_data = asdict(self)
        new_data["provenance"] = list(self.provenance)
        new_data["transformation_history"] = list(self.transformation_history)
        new_data["corroboration"] = list(self.corroboration)
        new_data["contradictions"] = list(self.contradictions)
        new_data["unavailable_fields"] = dict(self.unavailable_fields)

        for k, v in updates.items():
            if k in new_data:
                new_data[k] = v

        new_data["version"] = self.version + 1
        new_data["parent_version_id"] = f"{self.evidence_id}:v{self.version}"
        new_data["revision_time"] = datetime.now(timezone.utc)
        new_data["created_at"] = datetime.now(timezone.utc)
        new_data["transformation_history"].append({
            "operation": "version_update",
            "from_version": self.version,
            "to_version": new_data["version"],
            "justification": justification,
            "actor": actor,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "changed_fields": list(updates.keys()),
        })

        if isinstance(new_data.get("location"), dict):
            loc = new_data["location"]
            new_data["location"] = Location(**loc) if loc else None
        if isinstance(new_data.get("uncertainty"), dict):
            unc = new_data["uncertainty"]
            if unc:
                unc["type"] = UncertaintyType(unc["type"])
                new_data["uncertainty"] = Uncertainty(**unc)
            else:
                new_data["uncertainty"] = None
        if isinstance(new_data.get("epistemic_status"), str):
            new_data["epistemic_status"] = EpistemicStatus(new_data["epistemic_status"])

        def rebuild(items: list, cls: type) -> list:
            result = []
            for item in items:
                if isinstance(item, dict):
                    if "timestamp" in item and isinstance(item["timestamp"], str):
                        item["timestamp"] = datetime.fromisoformat(item["timestamp"])
                    if "input_refs" in item and isinstance(item["input_refs"], list):
                        item["input_refs"] = tuple(item["input_refs"])
                    result.append(cls(**item))
                else:
                    result.append(item)
            return result

        new_data["provenance"] = rebuild(new_data["provenance"], ProvenanceStep)
        new_data["corroboration"] = rebuild(new_data["corroboration"], CorroborationLink)
        new_data["contradictions"] = rebuild(new_data["contradictions"], ContradictionLink)
        return Evidence(**new_data)


def create_evidence(
    source_id: str,
    document_id: str,
    claim_id: str,
    value: Any,
    semantic_definition: str,
    source_reliability: float,
    source_independence: str,
    epistemic_status: EpistemicStatus = EpistemicStatus.ATTRIBUTED_CLAIM,
    event_id: Optional[str] = None,
    unit: Optional[str] = None,
    location: Optional[Location] = None,
    event_time: Optional[datetime] = None,
    publication_time: Optional[datetime] = None,
    methodology: Optional[str] = None,
    uncertainty: Optional[Uncertainty] = None,
    provenance: Optional[List[ProvenanceStep]] = None,
    unavailable_fields: Optional[Dict[str, str]] = None,
) -> Evidence:
    """Create evidence with explicit uncertainty; unknown uncertainty is preserved, not omitted."""
    now = datetime.now(timezone.utc)
    explicit_uncertainty = uncertainty or Uncertainty(
        type=UncertaintyType.UNKNOWN,
        qualitative="uncertainty not quantified by source",
    )
    return Evidence(
        evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
        version=1,
        source_id=source_id,
        document_id=document_id,
        claim_id=claim_id,
        event_id=event_id,
        value=value,
        unit=unit,
        semantic_definition=semantic_definition,
        location=location,
        event_time=event_time,
        publication_time=publication_time,
        ingestion_time=now,
        revision_time=None,
        detection_time=None,
        assessment_time=None,
        impact_time=None,
        methodology=methodology,
        source_reliability=source_reliability,
        source_independence=source_independence,
        uncertainty=explicit_uncertainty,
        provenance=provenance or [],
        transformation_history=[],
        corroboration=[],
        contradictions=[],
        epistemic_status=epistemic_status,
        unavailable_fields=unavailable_fields or {},
    )
