from datetime import datetime, timezone
from hashlib import sha256

from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.control_plane import EvidenceAssessment
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence, DecisionLifecycleEngine
from app.core.scientific.governance_signals import GovernanceDisposition
from app.core.scientific.intervention_independent_validation import ValidationLane, ValidationObservation

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def test_intervention_without_counterfactual_blocks_runtime(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    engine = DecisionLifecycleEngine(
        store,
        code_revision="test-revision",
        configuration=ConfigurationProvenance("test", "1", ("test-config",), {"mode": "test"}),
    )
    evidence = DecisionEvidence(
        "e1", "source1", "claim1", sha256(b"e1").hexdigest(), ("citation:e1",),
        BitemporalRef(NOW, None, NOW, None, "v1"), EvidenceAssessment("e1", "source1", 1.0),
    )
    context = DecisionContext("d-intervention", "operator", "short", (DecisionObjective("safety", 1.0),))
    option = DecisionOption("o1", (ScenarioOutcome("s1", 1.0, 1.0, 0.0),))
    observation = ValidationObservation(
        "validation-1", "prediction-1", ValidationLane.INTERVENTION, True, True, False, None,
        ("e1",), ("citation:e1",), NOW.isoformat(),
    )
    result = engine.execute(
        context, (option,), (evidence,), state_refs=("state1",), purpose="intervention-test",
        at=NOW, mode=DecisionMode.ROBUST, validation_observation=observation,
    )
    assert result.governance_signal is not None
    assert result.governance_signal.disposition is GovernanceDisposition.ABSTAIN
    assert any(reason.value == "intervention_counterfactual_required" for reason in result.governance_signal.reasons)
    assert any("intervention-validation:validation-1" in ref for node in result.lineage.nodes for ref in node.input_refs)
