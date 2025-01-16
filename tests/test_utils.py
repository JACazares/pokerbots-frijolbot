import pytest
from frijol_4.utils import compute_checkfold_win_probability
from frijol_4.helper_bot import FrijolBot
from frijol_4.skeleton.states import NUM_ROUNDS
import numpy as np

class MockBot(FrijolBot):
    def __init__(self, bankroll, round_num, big_blind):
        self._bankroll = bankroll
        self._round_num = round_num
        self._big_blind = big_blind

    def get_bankroll(self):
        return self._bankroll

    def get_round_num(self):
        return self._round_num

    def get_big_blind(self):
        return self._big_blind

def test_compute_checkfold_win_probability_high_bankroll():
    bot = MockBot(bankroll=1000, round_num=1, big_blind=True)
    probability = compute_checkfold_win_probability(bot)
    np.testing.assert_almost_equal(probability, 0)

def test_compute_checkfold_win_probability_low_bankroll():
    bot = MockBot(bankroll=10, round_num=1, big_blind=True)
    probability = compute_checkfold_win_probability(bot)
    np.testing.assert_almost_equal(probability, 0)

def test_compute_checkfold_win_probability_mid_game():
    bot = MockBot(bankroll=500, round_num=NUM_ROUNDS/2, big_blind=True)
    probability = compute_checkfold_win_probability(bot)

    np.testing.assert_almost_equal(probability, 0)

def test_compute_checkfold_win_probability_end_game():
    bot = MockBot(bankroll=500, round_num=NUM_ROUNDS, big_blind=True)
    probability = compute_checkfold_win_probability(bot)
    np.testing.assert_almost_equal(probability, 1.0)

if __name__ == '__main__':
    pytest.main()
