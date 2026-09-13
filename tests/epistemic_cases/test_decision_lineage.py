from backend.app.core.decision.lineage import DecisionLineage, LineageNode


def _lineage(execution_id: str) -> DecisionLineage:
    return DecisionLineage(
        decision_id="decision-1",
        nodes=(
            LineageNode(
                node_id="node-1",
                stage="inference",
                input_refs=("state:1",),
                output_refs=("inference:1",),
                evidence_refs=("evidence:1",),
                model_refs=("model:1",),
                policy_refs=("policy:1",),
                configuration_hash="config-1",
                code_revision="revision-1",
                as_of="2026-09-13T10:00:00+00:00",
                execution_id=execution_id,
            ),
            LineageNode(
                node_id="node-2",
                stage="decision",
                input_refs=("inference:1",),
                output_refs=("decision:1",),
                evidence_refs=("evidence:1",),
                model_refs=("model:1",),
                policy_refs=("policy:1",),
                configuration_hash="config-1",
                code_revision="revision-1",
                as_of="2026-09-13T10:00:01+00:00",
                execution_id=execution_id,
            ),
        ),
        terminal_disposition="recommend",
        semantic_identity="semantic-decision-1",
    )


def test_lineage_requires_explicit_nodes_and_dependencies() -> None:
    lineage = _lineage("run-1")
    assert len(lineage.nodes) == 2
    assert lineage.nodes[0].output_refs == ("inference:1",)
    assert lineage.nodes[1].input_refs == ("inference:1",)
    assert lineage.nodes[1].output_refs == ("decision:1",)


def test_semantic_lineage_identity_excludes_execution_id() -> None:
    first = _lineage("run-1")
    second = _lineage("run-2")

    assert first.semantic_fingerprint() == second.semantic_fingerprint()
    assert first.execution_fingerprint() != second.execution_fingerprint()
