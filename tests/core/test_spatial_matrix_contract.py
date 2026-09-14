import numpy as np
import pytest

from app.core.metrics import MetricInputError, territorial_spatial_lag


def test_spatial_weights_reject_nonzero_diagonal_instead_of_silently_rewriting_it():
    weights = [
        [0.5, 1.0],
        [1.0, 0.0],
    ]
    with pytest.raises(MetricInputError, match="diagonal|diagonal principal|autopesos|self"):
        territorial_spatial_lag([1.0, 2.0], weights)


def test_spatial_weights_can_be_asymmetric_when_each_row_has_valid_neighbours():
    weights = [
        [0.0, 2.0, 0.0],
        [1.0, 0.0, 3.0],
        [0.0, 4.0, 0.0],
    ]
    result = territorial_spatial_lag([1.0, 2.0, 5.0], weights)
    assert np.allclose(result, [2.0, 4.0, 2.0])
