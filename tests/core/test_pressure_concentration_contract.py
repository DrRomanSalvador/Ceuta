import pytest

from app.core.metrics import MetricInputError, territorial_pressure_concentration


def test_equal_multi_pressure_profile_is_undefined_without_territorial_variance():
    with pytest.raises(MetricInputError, match="varianza territorial nula"):
        territorial_pressure_concentration([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])
