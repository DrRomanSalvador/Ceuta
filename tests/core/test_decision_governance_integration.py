from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256

from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.control_plane import EvidenceAssessment
from app.core.decision.decision_system import DecisionContext, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence, DecisionLifecycleEngine
from app.core.runtime.model_governance import ModelGovernanceRecord
from app.core.scientific.governance_signals import GovernanceInput, GovernanceDisposition, GovernanceReason

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def engine(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    config = ConfigurationProvenance("test", "1", ("test-config",), {"mode": "test"})
    return DecisionLifecycleEngine(store, code_revision="test-revision", configuration=config), store, config


def evidence(disposition=None):
    assessment = EvidenceAssessment("e1", "source1", 1.0, disposition=disposition or EvidenceAssessment.__dataclass_fields__["disposition"].default)
    temporal = BitemporalRef(NOW, None, NOW, None, "v1")
    return DecisionEvidence("e1", "source1", "claim1", sha256(b"e1").hexdigest(), ("citation:e1",), temporal, assessment)


def inputs(configuration_hash, **changes):
    value = dict(
        evidence_ids=("e1",), provenance_refs=("citation:e1",), evidence_quality=0.9,
        independent_evidence_ratio=1.0, contradiction_ratio=0.0, credibility=0.9,
        mechanism_satisfied=True, provenance_valid=True, mechanism_integrity_valid=True,
        uncertainty=0.1, response_closure_complete=True, code_revision="test-revision",
        configuration_hash=configuration_hash, mechanism_ref="mechanism:test",
    )
    value.update(changes)
    return GovernanceInput(**value)


def model_release():
    record = ModelGovernanceRecord(
        model_id="model:test",
        version="1",
        code_hash=sha256(b"model-code").hexdigest(),
        data_snapshot_hash=sha256(b"model-data").hexdigest(),
        assumptions=("test assumption",),
        valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
        calibrated=True,
        validation_ref="validation:test",
        calibration_ref="calibration:test",
        approval_ref="approval:test",
    )
    return replace(record, release_hash=record.fingerprint())


def execute(engine, evidence_item, governance_input):
    context = DecisionContext("d1", "operator", "short", (DecisionObjective("safety", 1.0),))
    option = DecisionOption("o1", (ScenarioOutcome("s1", 1.0, 1.0, 0.0),), uncertainty=0.1)
    return engine.execute(
        context,
        (option,),
        (evidence_item,),
        state_refs=("state1",),
        scenario_refs=("scenario:test",),
        model_refs=("model:test",),
        model_releases={"model:test": model_release()},
        purpose="test decision",
        at=NOW,
        scientific_governance_input=governance_input,
    )


def test_clean_governance_reaches_recommendation(tmp_path):
    engine_instance, store, config = engine(tmp_path)
    result = execute(engine_instance, evidence(), inputs(config.fingerprint()))
    assert result.governance_signal is not None
    assert result.governance_signal.disposition is GovernanceDisposition.RELEASE
    assert result.disposition.value == "recommend"
    assert result.governance_signal.signal_id in result.lineage.nodes[-1].input_refs + result.lineage.nodes[-1].output_refs
    assert store.events("d1")


def test_manipulation_signal_forces_abstain(tmp_path):
    engine_instance, _, config = engine(tmp_path)
    result = execute(engine_instance, evidence(), inputs(config.fingerprint(), manipulation_flags=1))
    assert result.governance_signal.disposition is GovernanceDisposition.ABSTAIN
    assert GovernanceReason.STRATEGIC_MANIPULATION in result.governance_signal.reasons
    assert result.disposition.value == "abstain"
    assert "governance:strategic_manipulation" in result.degraded_reasons


def test_closure_incomplete_requires_review(tmp_path):
    engine_instance, _, config = engine(tmp_path)
    result = execute(engine_instance, evidence(), inputs(config.fingerprint(), response_closure_complete=False))
    assert result.governance_signal.disposition is GovernanceDisposition.REVIEW_REQUIRED
    assert GovernanceReason.RESPONSE_CLOSURE_INCOMPLETE in result.governance_signal.reasons
    assert result.disposition.value == "abstain"
