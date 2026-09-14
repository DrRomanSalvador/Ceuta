import math

import pytest

from app.core.final_epistemic_control import (
    FalsifiabilityStatus,
    OntologySignal,
    ProspectiveEvaluationProtocol,
    ProspectiveEvaluationResult,
    RealityAnchorAssessment,
)


def test_reality_anchor_rejects_nan_divergence() -> None:
    with pytest.raises(ValueError):
        RealityAnchorAssessment("x", FalsifiabilityStatus.PARTIAL, (), (), (), math.nan, False, ())


def test_established_reality_anchor_requires_external_conditions_and_evidence() -> None:
    with pytest.raises(ValueError, match="external evidence"):
        RealityAnchorAssessment("x", FalsifiabilityStatus.ESTABLISHED, (), (), (), 0.0, False, ())


def test_ontology_signal_rejects_non_finite_score() -> None:
    with pytest.raises(ValueError):
        OntologySignal("s1", "signal", math.nan, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_prospective_protocol_requires_complete_definition() -> None:
    with pytest.raises(ValueError):
        ProspectiveEvaluationProtocol("p1", "", "ceuta", "deployment", "12m", "rule", "baseline", "outcome", "1", "1", "1", "1", "1", True)


def test_prospective_result_rejects_non_finite_benefit() -> None:
    with pytest.raises(ValueError):
        ProspectiveEvaluationResult("p1", math.nan, True, "prospectively_validated")
