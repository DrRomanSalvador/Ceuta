import pytest

from app.core.scientific.knowledge import (
    EvidenceLevel,
    EvidenceRequirement,
    ScientificKnowledgeRegistry,
    ScientificSource,
    SourceType,
)


def test_registry_preserves_source_taxonomy_and_filters_by_evidence_level() -> None:
    registry = ScientificKnowledgeRegistry(
        (
            ScientificSource("high", "High", SourceType.SYSTEMATIC_REVIEW, EvidenceLevel.HIGH, domain="conflict"),
            ScientificSource("official", "Official", SourceType.GOVERNMENTAL, EvidenceLevel.OFFICIAL, domain="conflict"),
            ScientificSource("low", "Low", SourceType.OTHER, EvidenceLevel.LOWER_CONFIDENCE, domain="conflict"),
        )
    )
    selection = registry.select(
        EvidenceRequirement("prevention", domain="conflict", minimum_evidence_level=EvidenceLevel.OFFICIAL)
    )
    assert selection.source_ids == ("high", "official")
    assert all("low" not in trace for trace in selection.trace)


def test_duplicate_source_ids_are_rejected() -> None:
    source = ScientificSource("same", "A", SourceType.OTHER, EvidenceLevel.CONTEXTUAL)
    registry = ScientificKnowledgeRegistry((source,))
    with pytest.raises(ValueError):
        registry.add(source)


def test_selection_trace_preserves_epistemic_type() -> None:
    source = ScientificSource("s1", "Study", SourceType.METHODOLOGICAL, EvidenceLevel.METHODOLOGICAL)
    selection = ScientificKnowledgeRegistry((source,)).select(EvidenceRequirement("methods"))
    assert selection.trace == ("s1:methodological_statistical:methodological_evidence",)
