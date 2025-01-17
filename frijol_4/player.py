"""
Simple example pokerbot, written in Python.
"""

from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.runner import parse_args, run_bot

from helper_bot import FrijolBot

import random
import math
import numpy as np
import utils
from action_utils import CheckCall, CheckFold, RaiseCheckCall
import time

class Player(FrijolBot):
    """
    A pokerbot.
    """

    def __init__(self):
        """
        Called when a new game starts. Called exactly once.

        Arguments:
            Nothing.

        Returns:
            Nothing.
        """
        super().__init__()

    def handle_new_round(self, game_state, round_state, active):
        """
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
            game_state: the GameState object.
            round_state: the RoundState object.
            active: your player's index.

        Returns:
            Nothing.
        """
        self.game_state = game_state
        self.round_state = round_state
        self.terminal_state = None
        self.active = active
        if self.get_round_num() % 25 == 1:
            self.opponent_bounty_distribution = np.ones(13) / 13

        self.strategy = "frijol_4"

        target_bankroll = 12.5 * self.get_rounds_left() + (self.get_rounds_left() % 2) * (int(self.get_big_blind()) - 0.5)
        if self.get_bankroll() > target_bankroll:
            self.strategy = "checkfold"

        win_probability = utils.compute_checkfold_win_probability(self)
        if win_probability > 0.999:
            self.strategy = "checkfold"

        print(f"New Round {self.get_round_num()}")


    def handle_round_over(self, game_state, terminal_state, active):
        """
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
            game_state: the GameState object.
            terminal_state: the TerminalState object.
            active: your player's index.

        Returns:
            Nothing.
        """
        self.game_state = game_state
        self.round_state = None
        self.terminal_state = terminal_state
        self.active = active

        if self.get_my_delta() <= 0:
            self.opponent_bounty_distribution = utils.update_opponent_bounty_credences(self)

    def get_action(self, game_state, round_state, active):
        """
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
            game_state: the GameState object.
            round_state: the RoundState object.
            active: your player's index.

        Returns:
            Your action.
        """
        self.game_state = game_state
        self.round_state = round_state
        self.terminal_state = None
        self.active = active

        start_time = time.time()
        hand_strength = utils.estimate_hand_strength(self)
        pot = self.get_opponent_contribution() + self.get_my_contribution()
        self.pot_odds = utils.compute_pot_odds(self)
        print(f"Time to pot odds: {time.time() - start_time}")

        # print("pot size: ", pot, "with continue cost of", continue_cost)
        # print("pot_odds: ", round(continue_cost/(pot+continue_cost), 3))
        # print("pot_odds with bounty: ", round(pot_odds, 3))

        opening_raise=int(2.5*BIG_BLIND)
        three_bet_raise=int(3*pot+BIG_BLIND)

        if self.strategy == "checkfold":
            return CheckFold(self.get_legal_actions())

        if self.get_street() == 0:  # ..............................Preflop
            if hand_strength > self.pot_odds:
                if self.get_my_pip() == 0:
                    if hand_strength > 0.7:
                        var = random.random()
                        if var < 0.5:
                            return RaiseCheckCall(self, 3 * pot)
                        else: 
                            return CheckCall(self)
                else:
                    return CheckCall(self)
            else:
                return CheckFold(self)
                    
        if self.get_street() >= 3:  # ..............................Flop (+Turn+River)
            if hand_strength > self.pot_odds:
                if self.get_my_pip() == 0:
                    if hand_strength > 0.7:
                        var = random.random()
                        if var < 0.5:
                            return RaiseCheckCall(self, 3*pot)
                        else: 
                            return CheckCall(self)
                else:
                    return CheckCall(self)
            else:
                return CheckFold(self)
            
        # if self.get_street() == 4:  # ..............................Turn
        #     if hand_strength > 0.5:
        #         return CheckCall(self)
        #     else:
        #         return CheckFold(self)

        # if self.get_street() == 5:  # ..............................River
        #     if hand_strength > 0.5:
        #         return CheckCall(self)
        #     else:
        #         return CheckFold(self)

        return CheckCall(self)


if __name__ == "__main__":
    run_bot(Player(), parse_args())
