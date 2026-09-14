from backend.app.core.decision.lineage import DecisionLineage, LineageNode
from backend.app.core.decision.persistence import SQLiteDecisionStore


def _lineage() -> DecisionLineage:
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
                execution_id="run-1",
            ),
        ),
        terminal_disposition="recommend",
        semantic_identity="semantic-decision-1",
    )


def test_lineage_round_trips_through_sqlite(tmp_path) -> None:
    store = SQLiteDecisionStore(str(tmp_path / "decision.db"))
    lineage = _lineage()
    store.record_lineage(lineage)
    restored = store.lineage("decision-1")
    assert store.schema_version == 4
    assert restored is not None
    assert restored.semantic_fingerprint() == lineage.semantic_fingerprint()
    assert restored.execution_fingerprint() == lineage.execution_fingerprint()
    store.close()
