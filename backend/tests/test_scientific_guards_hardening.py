import pytest

from app.core.runtime.scientific_guards import ScientificIntegrityEngine


def test_scientific_gate_rejects_negative_contradiction_count() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ScientificIntegrityEngine().evaluate(
            observed=True,
            estimated=True,
            identifiable=True,
            predictive_calibrated=True,
            causal_identified=False,
            intervention_validated=False,
            contradictions=-1,
        )


def test_scientific_gate_requires_boolean_state_flags() -> None:
    with pytest.raises(TypeError, match="booleans"):
        ScientificIntegrityEngine().evaluate(
            observed="yes",
            estimated=True,
            identifiable=True,
            predictive_calibrated=True,
            causal_identified=False,
            intervention_validated=False,
        )
