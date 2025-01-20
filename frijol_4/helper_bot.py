from skeleton.bot import Bot
import skeleton.states as states
from io_utils import*
import numpy as np

class FrijolBot(Bot):
    def __init__(self):
        self.game_state = None
        self.round_state = None
        self.terminal_state = None
        self.active = None
        self.opponent_bounty_distribution = np.zeros(13)
        (self.BTN_opening_range, 
         self.BB_call_range_vs_open, 
         self.BB_3bet_range_vs_open, 
         self.BTN_call_range_vs_3bet, 
         self.BTN_4bet_range_vs_3bet, 
         self.BB_call_range_vs_4bet, 
         self.BB_5bet_range_vs_4bet)=read_starting_ranges("my_starting_ranges.csv")
        print(np.shape(self.BB_3bet_range_vs_open))
    
    def get_bankroll(self):
        return self.game_state.bankroll
    
    def get_game_clock(self):
        return self.game_state.game_clock
    
    def get_round_num(self):
        return self.game_state.round_num

    def get_rounds_left(self):
        return states.NUM_ROUNDS - self.game_state.round_num + 1

    def get_big_blind(self):
        return bool(self.active)
    
    def get_previous_state(self):
        return self.terminal_state.previous_state

    def get_legal_actions(self):
        return self.round_state.legal_actions()
    
    def get_street(self):
        if self.round_state is not None:
            return self.round_state.street
        return self.get_previous_state().street
    
    def get_my_cards(self):
        if self.round_state is not None:
            return self.round_state.hands[self.active]
        return self.get_previous_state().hands[self.active]

    def get_board_cards(self):
        if self.round_state is not None:
            return self.round_state.deck[:self.get_street()]
        return self.get_previous_state().deck[:self.get_street()]
    
    def get_opponent_cards(self):
        return self.get_previous_state().hands[1-self.active]
    
    def get_my_pip(self):
        return self.round_state.pips[self.active]

    def get_opponent_pip(self):
        return self.round_state.pips[1-self.active]
    
    def get_my_stack(self):
        return self.round_state.stacks[self.active]
    
    def get_opponent_stack(self):
        return self.round_state.stacks[1-self.active]
    
    def get_continue_cost(self):
        return self.get_opponent_pip() - self.get_my_pip()
    
    def get_my_bounty(self):
        return self.round_state.bounties[self.active]
    
    def get_my_contribution(self):
        return states.STARTING_STACK - self.get_my_stack()
    
    def get_opponent_contribution(self):
        return states.STARTING_STACK - self.get_opponent_stack()

    def get_my_delta(self):
        return self.terminal_state.deltas[self.active]
    
    def get_my_bounty_hit(self):
        return self.terminal_state.bounty_hits[self.active]
    
    def get_opponent_bounty_hit(self):
        return self.terminal_state.bounty_hits[1-self.active]
    
    def get_opponent_bounty_distribution(self):
        return self.opponent_bounty_distribution
    
    def get_raise_bounds(self):
        return self.round_state.raise_bounds()
    
    def get_opponent_range(self):
        return self.opponent_range
