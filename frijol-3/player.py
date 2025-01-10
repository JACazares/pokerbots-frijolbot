"""
Simple example pokerbot, written in Python.
"""

from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random
import math
import numpy as np
from utils import *


class Player(Bot):
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
        pass

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
        my_bankroll = (
            game_state.bankroll
        )  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        # my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        my_bounty = round_state.bounties[active]  # your current bounty rank
        rounds_left = 1001 - round_num  # Remaining rounds, including this one.
        if round_num%25==1:
            self.opp_bounty_distribution=[1/13]*13

        self.iwon = False  # Flag showing if the target bankroll is triggered
        target_bankroll = 12.5 * rounds_left + (rounds_left % 2) * (
            int(big_blind) - 0.5
        )  ## The bankroll at which always folding is a guaranteed winning strategy.
        if (
            my_bankroll > target_bankroll
        ):  # This routine always check-folds after reaching the guaranteed winning bankroll
            self.iwon = True
        self.winprob=compute_checkfold_winprob(rounds_left, my_bankroll, big_blind)
        if self.winprob>0.999:
            self.iwon = True
        print("round: ", round_num)
        print("my bounty: ", my_bounty)

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
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        board_cards = previous_state.deck[:street]  # the board cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        my_bounty_hit = terminal_state.bounty_hits[active]  # True if you hit bounty
        opponent_bounty_hit = terminal_state.bounty_hits[1-active] # True if opponent hit bounty
        if my_delta<=0: #If I lost
            print("my delta: ", my_delta)
            self.opp_bounty_distribution=update_opp_bounty_credences(self.opp_bounty_distribution, opponent_bounty_hit, street, my_cards, board_cards)
        print("Bounty probability distribution: ", [round(prob, 3) for prob in self.opp_bounty_distribution])

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
        legal_actions = (
            round_state.legal_actions()
        )  # the actions you are allowed to take
        street = (
            round_state.street
        )  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[
            active
        ]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_bounty = round_state.bounties[active]  # your current bounty rank
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        my_bankroll = (
            game_state.bankroll
        )  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        big_blind = bool(
            active
        )  # True if you are the big blind. Winnings are rounded up if you are the big blind, down if not
        if RaiseAction in legal_actions:
            min_raise, max_raise = (
                round_state.raise_bounds()
            )  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        else:
            min_raise = 0
            max_raise = 0

        if self.iwon:
            print("I won at round: ", round_num)
            return CheckFold(legal_actions)  # If you won, checkfold

        strength = estimate_strength(my_cards, board_cards, iters=200)
        print("street: ", street)
        print("strength: ", strength)

        pot=opp_contribution+my_contribution
        my_bounty_present = np.any([my_bounty == card for card in my_cards]) \
                          or np.any([my_bounty == card for card in board_cards])
        if my_bounty_present:
            pot_odds=continue_cost/(pot+continue_cost+0.5*opp_contribution+10)
        else:
            pot_odds=continue_cost/(pot+continue_cost)
            
        opening_raise=int(2.5*BIG_BLIND)
        three_bet_raise=int(3*pot+BIG_BLIND)

        if street == 0:  # ..............................Preflop
            if strength > pot_odds:
                if my_pip==0:
                    if strength > 0.7:
                        var=random.random()
                        if var<0.5:
                            return RaiseCheckCall(legal_actions, my_pip, round_state, 3*pot)
                        else: 
                            return CheckCall(legal_actions)
                else:
                    return CheckCall(legal_actions)
            else:
                return CheckFold(legal_actions)
                    
        if street >= 3:  # ..............................Flop (+Turn+River)
            if strength > pot_odds:
                if my_pip==0:
                    if strength > 0.7:
                        var=random.random()
                        if var<0.5:
                            return RaiseCheckCall(legal_actions, my_pip, round_state, 3*pot)
                        else: 
                            return CheckCall(legal_actions)
                else:
                    return CheckCall(legal_actions)
            else:
                return CheckFold(legal_actions)
            
        if street == 4:  # ..............................Turn
            if strength > 0.5:
                return CheckCall(legal_actions)
            else:
                return CheckFold(legal_actions)

        if street == 5:  # ..............................River
            if strength > 0.5:
                return CheckCall(legal_actions)
            else:
                return CheckFold(legal_actions)

        return CheckCall(legal_actions)


if __name__ == "__main__":
    run_bot(Player(), parse_args())
