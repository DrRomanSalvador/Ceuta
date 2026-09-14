import math

import pytest

from app.core.system_intelligence import PredictabilityAssessment, SystemAssessment


def test_system_assessment_rejects_non_finite_risk() -> None:
    with pytest.raises(ValueError, match="missing_data_risk must be finite"):
        SystemAssessment(
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


def test_predictability_assessment_rejects_non_finite_confidence() -> None:
    with pytest.raises(ValueError, match="predictability confidence must be finite"):
        PredictabilityAssessment(True, math.nan, (), False)
