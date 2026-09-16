from datetime import datetime, timezone
from hashlib import sha256

from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.control_plane import EvidenceAssessment
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence, DecisionLifecycleEngine
from app.core.scientific.governance_signals import GovernanceDisposition
from app.core.scientific.scientific_runtime_contract import (
    CausalRuntimeContract,
    FeatureSupport,
    NoveltyAssessment,
    ReferenceClassAssessment,
    ScientificRuntimeAssessment,
)

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def _evidence():
    assessment = EvidenceAssessment("e1", "source1", 1.0)
    return DecisionEvidence(
        "e1", "source1", "claim1", sha256(b"e1").hexdigest(), ("citation:e1",),
        BitemporalRef(NOW, None, NOW, None, "v1"), assessment,
    )


def _engine(tmp_path):
    return DecisionLifecycleEngine(
        SQLiteDecisionStore(str(tmp_path / "decision.sqlite")),
        code_revision="test-revision",
        configuration=ConfigurationProvenance("test", "1", ("test-config",), {"mode": "test"}),
    )


def _context():
    return DecisionContext("d-scientific", "operator", "short", (DecisionObjective("safety", 1.0),))


def _option():
    return DecisionOption("o1", (ScenarioOutcome("s1", 1.0, 1.0, 0.0),))


def test_causal_identification_gap_changes_canonical_runtime_to_abstain(tmp_path):
    assessment = ScientificRuntimeAssessment(
        "sra-causal", "d-scientific", ("e1",), ("citation:e1",),
        ReferenceClassAssessment("rc1", 100, 10, 1.0, 1.0),
        NoveltyAssessment((FeatureSupport("x", 0.0, 10.0, 5.0),)),
        CausalRuntimeContract("ATE", "intervention", "outcome", ("consistency", "positivity"), True),
        None, 0.1, "test-revision", "config-hash",
    )
    result = _engine(tmp_path).execute(
        _context(), (_option(),), (_evidence(),), state_refs=("state1",),
        purpose="scientific-runtime-test", at=NOW, mode=DecisionMode.ROBUST,
        scientific_runtime_assessment=assessment,
    )
    assert result.governance_signal is not None
    assert result.governance_signal.disposition is GovernanceDisposition.ABSTAIN
    assert any("causal_identification_unsatisfied" in reason.value for reason in result.governance_signal.reasons)
    assert result.disposition.value == "abstain"
    assert any("scientific-runtime:sra-causal" in ref for node in result.lineage.nodes for ref in node.input_refs)


def test_clean_scientific_contract_can_release(tmp_path):
    assessment = ScientificRuntimeAssessment(
        "sra-clean", "d-scientific", ("e1",), ("citation:e1",),
        ReferenceClassAssessment("rc1", 100, 10, 1.0, 1.0),
        NoveltyAssessment((FeatureSupport("x", 0.0, 10.0, 5.0, review_margin=0.01),)),
        None, None, 0.1, "test-revision", "config-hash",
    )
    result = _engine(tmp_path).execute(
        _context(), (_option(),), (_evidence(),), state_refs=("state1",),
        purpose="scientific-runtime-test", at=NOW, mode=DecisionMode.ROBUST,
        scientific_runtime_assessment=assessment,
    )
    assert result.governance_signal is not None
    assert result.governance_signal.disposition is GovernanceDisposition.RELEASE
