from datetime import datetime, timedelta, timezone
from hashlib import sha256

from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.control_plane import EvidenceAssessment
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence, DecisionLifecycleEngine
from app.core.scientific.governance_signals import GovernanceDisposition
from app.core.scientific.nonstationarity import NonStationarityMonitor, RegimeObservation

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def test_extrapolation_forces_runtime_abstention(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    engine = DecisionLifecycleEngine(
        store,
        code_revision="test-revision",
        configuration=ConfigurationProvenance("test", "1", ("test-config",), {"mode": "test"}),
    )
    assessment = NonStationarityMonitor(str(tmp_path / "ns.sqlite"), window=4).assess(
        tuple(
            RegimeObservation(NOW + timedelta(days=i), 1.0, 0.0, 2.0, "source1", f"p{i}")
            for i in range(8)
        ),
        deployment_value=3.0,
    )
    evidence_assessment = EvidenceAssessment("e1", "source1", 1.0)
    evidence = DecisionEvidence(
        "e1", "source1", "claim1", sha256(b"e1").hexdigest(), ("citation:e1",),
        BitemporalRef(NOW, None, NOW, None, "v1"), evidence_assessment,
    )
    context = DecisionContext("d-ns", "operator", "short", (DecisionObjective("safety", 1.0),))
    option = DecisionOption("o1", (ScenarioOutcome("s1", 1.0, 1.0, 0.0),))
    result = engine.execute(
        context, (option,), (evidence,), state_refs=("state1",), purpose="non-stationarity test",
        at=NOW, mode=DecisionMode.ROBUST, nonstationarity_assessment=assessment,
    )
    assert assessment.state == "abstain"
    assert result.governance_signal is not None
    assert result.governance_signal.disposition is GovernanceDisposition.ABSTAIN
    assert result.disposition.value == "abstain"
    assert any("nonstationarity:" in ref for node in result.lineage.nodes for ref in node.input_refs)
