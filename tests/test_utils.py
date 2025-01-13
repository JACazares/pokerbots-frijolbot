import pytest
import frijol_4.utils as utils

def test_compute_checkfold_win_probability():
    result = utils.compute_checkfold_win_probability(1, 100, True)
    expected_result = 1

    assert result == expected_result

# TODO: Add A LOT more unit tests here