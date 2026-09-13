from datetime import datetime, timezone

from app.core.calibration.drift import CalibrationDriftDetector
from app.core.calibration.model_governance import ModelGovernance, ModelRelease
from app.core.decision.decision_engine import DecisionEngine, DecisionOption
from app.core.decision.tradeoff_engine import TradeoffEngine
from app.core.governance.evidence_layer import EvidenceItem, EvidenceLayer, EvidenceLevel
from app.core.governance.information_firewall import Audience, InformationFirewall, InformationItem
from app.core.governance.llm_guard import LLMGuard
from app.core.governance.validation import CrossDomainConsistency, ModelDisagreement, UncertaintyPropagation
from app.core.ingestion.schema_drift import SchemaDriftDetector
from app.core.knowledge.versioning import KnowledgeStore, KnowledgeVersion
from app.core.serpiente.cascading_risk import CascadeRiskEngine
from app.core.serpiente.hypothesis_engine import CompetingHypothesisEngine, Hypothesis
from app.core.serpiente.scenario_engine import Scenario, ScenarioEngine
from app.core.spatial.flow_model import Flow, FlowMobilityModel
from app.core.spatial.spatial_engine import SpatialEngine, SpatialNode


def test_complex_system_engines_have_deterministic_boundaries() -> None:
    assert CascadeRiskEngine().propagate("a", {"a": (("b", 0.8),)}, 1.0)[-1].risk == 1.0
    hypotheses = (
        Hypothesis("h1", "one", ("e1",), (), (), "g1"),
        Hypothesis("h2", "two", (), ("e2",), ("e3",), "g2"),
    )
    assert CompetingHypothesisEngine().compare(hypotheses)[0].hypothesis_id == "h1"
    normalized = ScenarioEngine().normalize((Scenario("a", 2.0, (), ()), Scenario("b", 1.0, (), ()))
    assert abs(sum(s.probability for s in normalized) - 1.0) < 1e-12
    assert DecisionEngine().choose((DecisionOption("x", 1, 0, 0, 0.1),)).option_id == "x"
    assert DecisionEngine().choose((DecisionOption("x", 1, 0, 0, 0.9),), max_uncertainty=0.5).abstained
    assert TradeoffEngine().rank((("a", 2, 0, 0),))[0].option_id == "a"
    assert CalibrationDriftDetector().compare("m", baseline_error=1, current_error=2, threshold=0.5).alert
    assert ModelGovernance().approve(ModelRelease("m", "1", "NEW", 0.9), minimum_score=0.8).status == "APPROVED"
    assert SchemaDriftDetector().compare("s", {"a": "int"}, {"a": "str"}).detected
    now = datetime.now(timezone.utc)
    store = KnowledgeStore()
    store.append(KnowledgeVersion("v1", "e", now, None, ("evidence",)))
    assert store.as_of("e", now)
    assert FlowMobilityModel().normalize((Flow("a", "b", 2), Flow("b", "c", 2)))[0].volume == 0.5
    nodes = (SpatialNode("a", 0, 0, 1), SpatialNode("b", 0, 0.1, 0))
    assert SpatialEngine().propagate(nodes, radius=1)[1].risk == 1
    assert CrossDomainConsistency().check((1, 1.01), tolerance=0.02)
    assert ModelDisagreement().score((1, 3)) == 1
    assert UncertaintyPropagation().combine((3, 4)) == 5


def test_governance_boundaries_are_fail_closed() -> None:
    assert not LLMGuard.can_mutate_state()
    firewall = InformationFirewall()
    owner = InformationItem("x", Audience.OWNER, "private", ("e",))
    try:
        firewall.release(owner, Audience.PUBLIC)
    except PermissionError:
        pass
    else:
        raise AssertionError("OWNER information crossed the public firewall")
    assert EvidenceLayer().insufficient_evidence_message()
    fact = EvidenceItem("e", EvidenceLevel.FACT, "observed", ("s",), "2026-01-01")
    assert EvidenceLayer().stratify((fact,))[0].level is EvidenceLevel.FACT
