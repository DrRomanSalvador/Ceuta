import pytest

from app.core.evidence.uncertainty_model import UncertaintyVector, propagate_uncertainty


def test_uncertainty_components_are_not_collapsed() -> None:
    result = propagate_uncertainty(
        (
            UncertaintyVector(measurement=0.8, model=0.2),
            UncertaintyVector(measurement=0.4, structural=0.9),
        ),
        source_refs=("a", "b"),
    )
    assert result.components.measurement == pytest.approx(0.8)
    assert result.components.structural == pytest.approx(0.9)
    assert result.components.maximum == pytest.approx(0.9)
    assert set(result.components.dominant_components()) == {"structural", "measurement"}
    assert result.abstention_required is True
