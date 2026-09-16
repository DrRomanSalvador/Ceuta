from datetime import datetime, timezone

import pytest

from app.core.decision.persistence import SQLiteDecisionStore
from app.core.scientific.governance_signals import (
    GovernanceDisposition,
    GovernanceInput,
    GovernanceReason,
    ScientificGovernance,
)


NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def good(**overrides):
    data = dict(
        evidence_ids=("e1",), provenance_refs=("source:e1",), evidence_quality=0.9,
        independent_evidence_ratio=0.9, contradiction_ratio=0.0, credibility=0.9,
        mechanism_satisfied=True, provenance_valid=True, mechanism_integrity_valid=True,
        uncertainty=0.1, response_closure_complete=True, code_revision="abc123",
        configuration_hash="cfg123", mechanism_ref="mechanism:1",
    )
    data.update(overrides)
    return GovernanceInput(**data)


def test_clean_path_releases_and_persists(tmp_path):
    db = tmp_path / "governance.sqlite"
    gov = ScientificGovernance(storage_path=str(db))
    signal = gov.evaluate("d1", good(), created_at=NOW)
    assert signal.disposition is GovernanceDisposition.RELEASE
    assert signal.effect == "release"
    assert GovernanceReason.INTEGRITY_VERIFIED in signal.reasons

    restored = ScientificGovernance(storage_path=str(db))
    assert restored.get(signal.signal_id).audit_hash == signal.audit_hash


def test_fingerprint_is_strict_and_reproducible():
    value = good()
    first = ScientificGovernance._fingerprint("decision-1", value)
    second = ScientificGovernance._fingerprint("decision-1", value)
    assert first == second
    assert len(first) == 64
    with pytest.raises(ValueError):
        ScientificGovernance._fingerprint("decision-1", good(evidence_quality=float("nan")))


def test_decision_store_binds_default_governance_persistence(tmp_path):
    db = tmp_path / "decision.sqlite"
    store = SQLiteDecisionStore(str(db))
    gov = ScientificGovernance()
    signal = gov.evaluate("d-store", good(), created_at=NOW)
    assert signal.disposition is GovernanceDisposition.RELEASE
    restored = ScientificGovernance()
    assert restored.get(signal.signal_id).decision_id == "d-store"
    store.close()


def test_quality_and_conflict_require_review():
    gov = ScientificGovernance()
    signal = gov.evaluate("d2", good(evidence_quality=0.4, contradiction_ratio=0.6, model_conflict=True), created_at=NOW)
    assert signal.disposition is GovernanceDisposition.REVIEW_REQUIRED
    assert GovernanceReason.EVIDENCE_INSUFFICIENT in signal.reasons
    assert GovernanceReason.EVIDENCE_CONTRADICTORY in signal.reasons
    assert GovernanceReason.MODEL_CONFLICT in signal.reasons


def test_integrity_or_manipulation_abstains():
    gov = ScientificGovernance()
    for value in (
        good(provenance_valid=False),
        good(mechanism_satisfied=False),
        good(manipulation_flags=1),
        good(collusion_flags=1),
        good(uncertainty=0.95),
    ):
        signal = gov.evaluate("d-hard-" + str(hash(str(value))), value, created_at=NOW)
        assert signal.disposition is GovernanceDisposition.ABSTAIN
        assert signal.effect == "do_not_release"


def test_response_closure_blocks_release_but_not_truth_claim():
    gov = ScientificGovernance()
    signal = gov.evaluate("d3", good(response_closure_complete=False), created_at=NOW)
    assert signal.disposition is GovernanceDisposition.REVIEW_REQUIRED
    assert GovernanceReason.RESPONSE_CLOSURE_INCOMPLETE in signal.reasons


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        good(independent_evidence_ratio=1.2)
