import pytest

from app.core.system.uncertainty_state import UncertaintyState


def test_uncertainty_components_remain_distinct() -> None:
    state = UncertaintyState(measurement=0.8, structural=0.9, model=0.2)
    assert state.conservative_upper_bound == pytest.approx(0.9)
    assert set(state.dominant_components()) == {"measurement", "structural"}


def test_uncertainty_merge_is_componentwise_conservative() -> None:
    merged = UncertaintyState(measurement=0.2, state=0.3).merge_conservative(
        UncertaintyState(measurement=0.7, structural=0.6)
    )
    assert merged.measurement == pytest.approx(0.7)
    assert merged.state == pytest.approx(0.3)
    assert merged.structural == pytest.approx(0.6)
