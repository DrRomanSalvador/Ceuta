import pytest

from app.core.scientific.evidence_bridge import ForecastEvidenceBinding, validate_binding
from app.core.scientific.knowledge import EvidenceLevel, EvidenceRequirement, ScientificKnowledgeRegistry, ScientificSource, SourceType


def test_forecast_binding_requires_declared_scientific_sources():
    registry = ScientificKnowledgeRegistry([
        ScientificSource(
            source_id="method-1",
            title="Forecast methodology",
            source_type=SourceType.METHODOLOGICAL,
            evidence_level=EvidenceLevel.METHODOLOGICAL,
            domain="forecasting",
            question_types=("predictive",),
            response_types=("decision_support",),
        )
    ])
    binding = ForecastEvidenceBinding(
        evidence_ids=("runtime-e1",),
        scientific_source_ids=("method-1",),
        evidence_fingerprint="fp-1",
        requirement=EvidenceRequirement(
            question_type="predictive",
            domain="forecasting",
            response_type="decision_support",
            minimum_evidence_level=EvidenceLevel.METHODOLOGICAL,
        ),
    )
    trace = validate_binding(binding, registry)
    assert trace == ("method-1:methodological_statistical:methodological_evidence",)
    assert len(binding.provenance_hash) == 64


def test_binding_rejects_source_outside_requirement():
    registry = ScientificKnowledgeRegistry([
        ScientificSource(
            source_id="wrong",
            title="Wrong domain",
            source_type=SourceType.OBSERVATIONAL,
            evidence_level=EvidenceLevel.CONTEXTUAL,
            domain="other",
        )
    ])
    binding = ForecastEvidenceBinding(
        evidence_ids=("runtime-e1",),
        scientific_source_ids=("wrong",),
        evidence_fingerprint="fp-1",
        requirement=EvidenceRequirement("predictive", "forecasting", "decision_support"),
    )
    with pytest.raises(ValueError):
        validate_binding(binding, registry)
