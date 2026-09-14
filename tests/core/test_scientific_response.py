from app.core.scientific.knowledge import (
    EvidenceLevel,
    EvidenceRequirement,
    ScientificKnowledgeRegistry,
    ScientificSource,
    SourceType,
)


def test_selection_filters_question_and_response_requirements() -> None:
    registry = ScientificKnowledgeRegistry(
        (
            ScientificSource(
                "good",
                "Controlled study",
                SourceType.CONTROLLED_EVIDENCE,
                EvidenceLevel.HIGH,
                domain="health",
                question_types=("effectiveness",),
                response_types=("decision_support",),
                limitation="single context",
            ),
            ScientificSource(
                "wrong-question",
                "Methodological study",
                SourceType.METHODOLOGICAL,
                EvidenceLevel.METHODOLOGICAL,
                domain="health",
                question_types=("measurement",),
                response_types=("decision_support",),
            ),
            ScientificSource(
                "wrong-response",
                "Controlled study",
                SourceType.CONTROLLED_EVIDENCE,
                EvidenceLevel.HIGH,
                domain="health",
                question_types=("effectiveness",),
                response_types=("policy",),
            ),
        )
    )
    response = registry.respond(
        EvidenceRequirement(
            question_type="effectiveness",
            domain="health",
            response_type="decision_support",
            minimum_evidence_level=EvidenceLevel.METHODOLOGICAL,
        )
    )
    assert response.source_ids == ("good",)
    assert response.evidence_trace == (
        "good:randomized_controlled_evidence:high_level_evidence",
    )
    assert response.limitations == ("good: single context",)
    assert response.uncertainty
