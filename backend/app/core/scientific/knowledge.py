"""Structured scientific source knowledge and response-oriented evidence selection.

The registry keeps heterogeneous source types together while preserving their
epistemic classification. Selection never upgrades evidence merely because more
sources are present; source type and declared evidence level remain explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class SourceType(StrEnum):
    SYSTEMATIC_REVIEW = "systematic_review_meta_analysis"
    CONTROLLED_EVIDENCE = "randomized_controlled_evidence"
    OBSERVATIONAL = "observational_evidence"
    LONGITUDINAL = "longitudinal_cohort_evidence"
    METHODOLOGICAL = "methodological_statistical"
    GUIDELINE = "scientific_consensus_guideline"
    GOVERNMENTAL = "governmental_official"
    INTERNATIONAL = "european_international_official"
    STANDARD = "technical_standard"
    TECHNICAL_REPORT = "institutional_technical_report"
    OTHER = "other"


class EvidenceLevel(StrEnum):
    HIGH = "high_level_evidence"
    OFFICIAL = "official_factual_source"
    METHODOLOGICAL = "methodological_evidence"
    CONTEXTUAL = "contextual_evidence"
    LOWER_CONFIDENCE = "lower_confidence_material"


@dataclass(frozen=True, slots=True)
class ScientificSource:
    source_id: str
    title: str
    source_type: SourceType
    evidence_level: EvidenceLevel
    authors: tuple[str, ...] = ()
    publication: str = ""
    year: int | None = None
    identifier: str = ""
    official_url: str = ""
    methodology: str = ""
    population_context: str = ""
    domain: str = ""
    question_types: tuple[str, ...] = ()
    response_types: tuple[str, ...] = ()
    finding: str = ""
    limitation: str = ""
    applicability: str = ""
    ceutia_component: str = ""
    serpiente_component: str = ""
    implementation_implication: str = ""
    validation_requirement: str = ""
    provenance: str = ""

    def __post_init__(self) -> None:
        if not self.source_id or not self.title:
            raise ValueError("source_id and title are required")
        if self.year is not None and not 0 < self.year <= 3000:
            raise ValueError("year must be a plausible publication year")


@dataclass(frozen=True, slots=True)
class EvidenceRequirement:
    question_type: str
    domain: str = ""
    response_type: str = ""
    minimum_evidence_level: EvidenceLevel = EvidenceLevel.CONTEXTUAL


@dataclass(frozen=True, slots=True)
class EvidenceSelection:
    source_ids: tuple[str, ...]
    trace: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScientificResponse:
    question_type: str
    domain: str
    response_type: str
    source_ids: tuple[str, ...]
    evidence_trace: tuple[str, ...]
    limitations: tuple[str, ...]
    uncertainty: tuple[str, ...]


_LEVEL_RANK = {
    EvidenceLevel.HIGH: 5,
    EvidenceLevel.OFFICIAL: 4,
    EvidenceLevel.METHODOLOGICAL: 3,
    EvidenceLevel.CONTEXTUAL: 2,
    EvidenceLevel.LOWER_CONFIDENCE: 1,
}


class ScientificKnowledgeRegistry:
    """In-memory scientific corpus with deterministic, traceable selection."""

    def __init__(self, sources: Iterable[ScientificSource] = ()) -> None:
        self._sources: dict[str, ScientificSource] = {}
        for source in sources:
            self.add(source)

    def add(self, source: ScientificSource) -> None:
        if source.source_id in self._sources:
            raise ValueError(f"duplicate source_id: {source.source_id}")
        self._sources[source.source_id] = source

    def get(self, source_id: str) -> ScientificSource:
        return self._sources[source_id]

    def all(self) -> tuple[ScientificSource, ...]:
        return tuple(self._sources.values())

    def select(self, requirement: EvidenceRequirement) -> EvidenceSelection:
        minimum = _LEVEL_RANK[requirement.minimum_evidence_level]
        candidates = [
            source
            for source in self._sources.values()
            if _LEVEL_RANK[source.evidence_level] >= minimum
            and (not requirement.domain or source.domain == requirement.domain)
            and (not source.question_types or requirement.question_type in source.question_types)
            and (not source.response_types or requirement.response_type in source.response_types)
        ]
        candidates.sort(
            key=lambda source: (
                source.domain == requirement.domain if requirement.domain else False,
                requirement.question_type in source.question_types if source.question_types else False,
                requirement.response_type in source.response_types if source.response_types else False,
                _LEVEL_RANK[source.evidence_level],
                source.year or 0,
                source.source_id,
            ),
            reverse=True,
        )
        limitations = tuple(
            f"{source.source_id}: {source.limitation}"
            for source in candidates
            if source.limitation
        )
        trace = tuple(
            f"{source.source_id}:{source.source_type.value}:{source.evidence_level.value}"
            for source in candidates
        )
        return EvidenceSelection(
            source_ids=tuple(source.source_id for source in candidates),
            trace=trace,
            limitations=limitations,
        )

    def respond(self, requirement: EvidenceRequirement) -> ScientificResponse:
        selection = self.select(requirement)
        uncertainty = tuple(
            f"{source_id}: applicability and limitations must be interpreted from the source context"
            for source_id in selection.source_ids
            if self.get(source_id).limitation or self.get(source_id).applicability
        )
        return ScientificResponse(
            question_type=requirement.question_type,
            domain=requirement.domain,
            response_type=requirement.response_type,
            source_ids=selection.source_ids,
            evidence_trace=selection.trace,
            limitations=selection.limitations,
            uncertainty=uncertainty,
        )


__all__ = [
    "EvidenceLevel",
    "EvidenceRequirement",
    "EvidenceSelection",
    "ScientificKnowledgeRegistry",
    "ScientificResponse",
    "ScientificSource",
    "SourceType",
]
