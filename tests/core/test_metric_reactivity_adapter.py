from app.core.scientific.governance_signals import GovernanceDisposition, ScientificGovernance
from app.core.scientific.metric_reactivity_adapter import MetricReactivityGovernanceAdapter
from app.core.scientific.metric_reactivity import GamingDiagnostics


def _diag(compromised: bool) -> GamingDiagnostics:
    flags = ("indicator_validity_compromised",) if compromised else ()
    return GamingDiagnostics(20, 0.1, 0.0, 0.1, 0.0, 20, 0.8 if compromised else 0.1, flags, 0.2 if compromised else 0.9)


def test_compromised_indicator_cannot_release(tmp_path):
    adapter = MetricReactivityGovernanceAdapter("rev", "cfg")
    governance = ScientificGovernance(storage_path=str(tmp_path / "gov.sqlite"))
    value = adapter.to_input(_diag(True), evidence_ids=("e1",), provenance_refs=("p1",), evidence_quality=0.9, independent_evidence_ratio=0.9, contradiction_ratio=0.0)
    signal = governance.evaluate("decision-1", value)
    assert signal.disposition == GovernanceDisposition.ABSTAIN


def test_clean_indicator_can_release(tmp_path):
    adapter = MetricReactivityGovernanceAdapter("rev", "cfg")
    governance = ScientificGovernance(storage_path=str(tmp_path / "gov.sqlite"))
    value = adapter.to_input(_diag(False), evidence_ids=("e1",), provenance_refs=("p1",), evidence_quality=0.9, independent_evidence_ratio=0.9, contradiction_ratio=0.0)
    signal = governance.evaluate("decision-1", value)
    assert signal.disposition == GovernanceDisposition.RELEASE
