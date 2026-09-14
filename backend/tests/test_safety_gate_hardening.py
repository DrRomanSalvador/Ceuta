import pytest

from app.core.runtime.safety import SafetyEngine


def test_safety_gate_requires_boolean_inputs() -> None:
    with pytest.raises(TypeError, match="booleans"):
        SafetyEngine().evaluate(
            observable="yes",
            identifiable=True,
            calibrated=True,
            source_integrity=True,
            model_valid=True,
        )
