import pytest

from app.core.metrics import territorial_pressure_concentration


def test_equal_multi_pressure_profile_has_uniform_concentration():
    assert territorial_pressure_concentration([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]) == pytest.approx(1.0 / 3.0)
