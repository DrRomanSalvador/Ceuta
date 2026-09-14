import pytest

from app.core.metrics import MetricInputError, territorial_spatial_lag


def test_spatial_weights_reject_nonzero_diagonal_instead_of_silently_rewriting_it():
    weights = [
        [0.5, 1.0],
        [1.0, 0.0],
    ]
    with pytest.raises(MetricInputError, match="diagonal|diagonal principal|autopesos|self"):
        territorial_spatial_lag([1.0, 2.0], weights)
