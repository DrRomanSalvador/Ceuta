from app.core.decision.control_plane import DecisionOutcome
from app.core.decision.persistence import SQLiteDecisionStore


def outcome(utility: float = 1.0) -> DecisionOutcome:
    return DecisionOutcome(
        decision_id="d1",
        option_id="o1",
        expected_utility=1.0,
        observed_utility=utility,
        expected_harm=0.0,
        observed_harm=0.0,
        outcome_at="2026-09-15T00:00:00+00:00",
    )


def test_outcome_duplicate_is_idempotent_but_conflicting_write_fails(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    first = outcome()
    store.record_outcome(first)
    store.record_outcome(first)
    assert store.outcomes("d1") == (first,)
    try:
        store.record_outcome(outcome(utility=0.2))
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting outcome overwrote persisted history")
    assert store.outcomes("d1") == (first,)
    store.close()


def test_lineage_duplicate_is_idempotent_but_conflicting_write_fails(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    from app.core.decision.lineage import DecisionLineage, LineageNode

    def lineage(ref: str) -> DecisionLineage:
        return DecisionLineage(
            decision_id="d1",
            nodes=(LineageNode("n1", "state", evidence_refs=(ref,)),),
            terminal_disposition="recommend",
            semantic_identity="semantic:d1",
        )

    first = lineage("e1")
    store.record_lineage(first)
    store.record_lineage(first)
    assert store.lineage("d1").execution_fingerprint() == first.execution_fingerprint()
    try:
        store.record_lineage(lineage("e2"))
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting lineage overwrote persisted history")
    assert store.lineage("d1").execution_fingerprint() == first.execution_fingerprint()
    store.close()
