import math

from app.core.runtime.system_gate import SystemGateDisposition, SystemIntelligenceGate
from app.core.system_intelligence import PredictabilityAssessment, SystemAssessment


def test_system_gate_abstains_on_non_finite_risk() -> None:
    assessment = SystemAssessment(
        observable=True,
        identifiable=True,
        predictability=PredictabilityAssessment(True, 0.9, (), False),
        model_disagreement=None,
        missing_data_risk=math.nan,
        measurement_process_risk=0.0,
        spatial_dependency=False,
        network_dependency=False,
        regime_changed=False,
        abstain=False,
        reasons=(),
    )
    result = SystemIntelligenceGate().evaluate(assessment)
    assert result.disposition is SystemGateDisposition.ABSTAIN


def test_system_gate_abstains_on_non_finite_predictability_confidence() -> None:
    assessment = SystemAssessment(
        observable=True,
        identifiable=True,
        predictability=PredictabilityAssessment(True, math.nan, (), False),
        model_disagreement=None,
        missing_data_risk=0.0,
        measurement_process_risk=0.0,
        spatial_dependency=False,
        network_dependency=False,
        regime_changed=False,
        abstain=False,
        reasons=(),
    )
    result = SystemIntelligenceGate().evaluate(assessment)
    assert result.disposition is SystemGateDisposition.ABSTAIN
