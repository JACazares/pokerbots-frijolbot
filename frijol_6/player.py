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
from action_utils import CheckCall, CheckFold, RaiseCheckCall, mixed_strategy
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
        self.previous_street=0
        self.opponent_called=False

        self.opponent_actions = []
        self.previously_raised = False
        self.last_opponent_action = 0

        if self.get_round_num() % 25 == 1:
            self.opponent_bounty_distribution = np.ones(13) / 13
        self.opponent_range = (np.ones([52, 52])-np.diag(np.ones(52)))*2/(52*51)

        self.opponent_range = utils.update_opponent_range(self)

        self.strategy = max(self.strategy_bankrolls, key=lambda x: self.strategy_bankrolls[x])

        target_bankroll = 12.5 * self.get_rounds_left() + (self.get_rounds_left() % 2) * (int(self.get_big_blind()) - 0.5)
        if self.get_bankroll() > target_bankroll:
            self.strategy = "checkfold"

        win_probability = utils.compute_checkfold_win_probability(self)
        if win_probability > 0.999:
            self.strategy = "checkfold"

        print(" ")
        print(" ")
        print("ROUND", self.get_round_num(), "--------------------------------------------------------------------------------------------------------------------------------")
        print("Big blind: ", self.get_big_blind(), "....... My bounty: ", self.get_my_bounty())
        print("My bankroll: ", self.get_bankroll(), "with probability", round(win_probability, 3), "of winning.")
        print("my_cards: ", self.get_my_cards())
        print("Strategy: ", self.strategy)


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
        my_delta=self.get_my_delta()
        self.strategy_bankrolls[self.strategy]+=my_delta
        print("----------- Results ----------")
        print("New strategy bankrolls: ", self.strategy_bankrolls)
        if my_delta>0:
            print("Winner: MYSELF with bounty ", self.get_my_bounty_hit())
        if my_delta<=0: #If I lost
            if my_delta<0:
                print("Winner: OPPONENT with bounty ", self.get_opponent_bounty_hit())
            if my_delta==0:
                print("Winner: TIE with bounties", self.get_my_bounty_hit(), "for me and", self.get_opponent_bounty_hit(), "for opponent")
            self.opponent_bounty_distribution = utils.update_opponent_bounty_credences(self)
        print("Opponent bounty probability distribution: ", [round(prob, 3) for prob in self.opponent_bounty_distribution])

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
        big_blind = self.get_big_blind() #True if you are the big blind
        my_pip = self.get_my_pip()
        opp_pip = self.get_opponent_pip()
        utils.update_opponent_actions(self)

        if my_pip==0 or self.get_street()==0 and (my_pip==1 or my_pip==2): 
            print("")
            if self.get_street()==0:
                print("------PREFLOP------")
            if self.get_street()==3:
                print("-------FLOP--------")
            if self.get_street()==4:
                print("-------TURN--------")
            if self.get_street()==5:
                print("-------RIVER-------")
            print("board cards: ", self.get_board_cards())

        while self.last_opponent_action < len(self.opponent_actions):
            print("Opponent action: ", self.opponent_actions[self.last_opponent_action])
            self.last_opponent_action += 1

        if self.previous_street is not self.get_street():
            self.opponent_called = True
        else: 
            self.opponent_called = False 
        self.previous_street = self.get_street()

        #start_time = time.time()
        self.opponent_range = utils.update_opponent_range(self)
        #print("update opp_range time: ", time.time()-start_time)

        pot = self.get_opponent_contribution() + self.get_my_contribution()
        self.pot_odds = utils.compute_pot_odds(self)

       # print(f"Time to pot odds: {time.time() - start_time}")

        print("pot size: ", pot, "with continue cost of", self.get_continue_cost())
        print("pot_odds: ", round(self.get_continue_cost()/(pot+self.get_continue_cost()), 3))
        print("pot_odds with bounty: ", round(self.pot_odds, 3))

        opening_raise=int(2.5*BIG_BLIND)
        three_bet_raise=int(3*pot+BIG_BLIND)

        if self.strategy == "checkfold":
            return CheckFold(self)

        if self.get_street() == 0:  # ..............................Preflop
            print("BIG BLIND: ",  big_blind)
            if not big_blind: #If you are the small blind
                if my_pip==1:
                    raise_range_matrix = self.BTN_opening_range
                    raise_amount = int(2.5*BIG_BLIND)
                    call_range_matrix = np.zeros([13, 13])
                else:
                    raise_range_matrix = self.BTN_4bet_range_vs_3bet
                    call_range_matrix = self.BTN_call_range_vs_3bet
                    raise_amount = int(3*pot+BIG_BLIND)
            else:
                if my_pip==2 and opp_pip==2: #Never plays for free (weird)
                    raise_range_matrix = self.BTN_opening_range
                    raise_amount = int(2.5*BIG_BLIND)
                    call_range_matrix = np.zeros([13, 13])
                elif my_pip==2 and opp_pip<50:
                    raise_range_matrix = self.BB_3bet_range_vs_open
                    call_range_matrix = self.BB_call_range_vs_open
                    raise_amount = int(3*pot+BIG_BLIND)
                else:
                    raise_range_matrix = self.BB_5bet_range_vs_4bet
                    call_range_matrix = self.BB_call_range_vs_4bet
                    raise_amount = int(2.5*pot+BIG_BLIND)
            fold_probability, call_probability, raise_probability = utils.preflop_action_distribution(self, call_range_matrix, raise_range_matrix)
            print("Preflop strategy (Fold, Call, Raise): ", round(fold_probability, 3), round(call_probability, 3), round(raise_probability, 3))
            return mixed_strategy(self, fold_probability, call_probability, raise_amount)

        if self.get_street() >= 3:  # ..............................Flop (+Turn+River)
            #start_time = time.time()
            if self.strategy == "conservative":
                raise_probs=[0.8, 0.5]
                raise_threshold = [0.85, 0.95]
                odds_offset = 0.15
            elif self.strategy == "mid":
                raise_probs=[0.9, 0.7]
                raise_threshold = [0.75, 0.9]
                odds_offset = 0.05
            elif self.strategy =="aggressive":
                raise_probs=[0.95, 0.85]
                raise_threshold = [0.65, 0.75]
                odds_offset = -0.02
            else:
                print("error")
                return CheckFold()

            hand_strength = utils.estimate_hand_strength(self, bounty_strength=0)
            print("hand strength:",  hand_strength)
            #print("handstrength time: ", time.time()-start_time)
            if hand_strength > self.pot_odds + odds_offset:
                if self.get_my_pip() == 0:
                    if hand_strength > 1-(350-pot)*(1-raise_threshold[0])/325:
                        var = random.random()
                        if var < raise_probs[0]:
                            return RaiseCheckCall(self, 3*pot)
                        else: 
                            return CheckCall(self)
                    return CheckCall(self)
                elif self.get_my_pip() < 4*pot:
                    if hand_strength > 1-(350-pot)*(1-raise_threshold[1])/325:
                        var = random.random()
                        if var < raise_probs[1]: 
                            return RaiseCheckCall(self, 3*pot)
                        else: 
                            return CheckCall(self)
                    return CheckCall(self)
                else:
                    CheckCall(self)
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
        print("No action")
        return CheckCall(self)


if __name__ == "__main__":
    run_bot(Player(), parse_args())
