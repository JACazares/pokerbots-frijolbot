import scipy.special
import math
import numpy as np
import eval7
from itertools import combinations
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random

def RaiseCheckCall(legal_actions, my_pip, round_state, raise_amount):
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
        min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
        max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        if raise_amount>max_raise:
            raise_amount=max_raise
        if raise_amount<min_raise:
            raise_amount=min_raise
        return RaiseAction(raise_amount)
    return CheckCall()

def CheckFold(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return FoldAction()

def CheckCall(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return CallAction() 

def compute_checkfold_winprob(rounds_left, bankroll, big_blind):
    '''
        Computes the probability of winning by only checking or folding given a current bankroll and number of rounds left (including this one).

        Inputs: 
        rounds_left: The number of rounds left to play, including this one.
        bankroll: Net wins or losses so far
        big_blind: True if you are the big blind, False otherwise

        Outputs: 
        A number from 0 to 1 indicating the probability of winning with the check-fold strategy from now on. 

        Note that this function can be used backwards, by inputting the negative bankroll and the negation of big_blind. 
        This indicates the probability of you losing if the opponent does the check-fold strategy.  
    '''
    bounties_to_win=math.ceil((bankroll-3*rounds_left/2-(rounds_left%2)*(int(big_blind)-0.5))/11)-1 #How many times the opponent can hit the bounty and you still win
    if bounties_to_win>rounds_left: #Bring that number to rounds_left if it is too big. Of course. In that case the probability will just be 1
        bounties_to_win=rounds_left
    if bounties_to_win<0:   #If it is negative, you have other problems
        bounties_to_win=0
    winning_cases=np.arange(bounties_to_win+1)
    success_rate=1-48*47/(52*51)
    probabilities=np.array([scipy.special.comb(rounds_left, case, exact=True) for case in winning_cases])
    probabilities=probabilities*(success_rate**winning_cases)*(1-success_rate)**(rounds_left-winning_cases)
    return np.sum(probabilities)

def estimate_strength(hole, board=[], iters=200):
    '''
        Performs a Montecarlo search to approximate the strength of a hand. 
        
        Inputs: 
        hole (list of strings): A list of your two hole cards
        board (list of strings): A (possibly empty) list of the board cards
        iters (int): Number of iterations to run. More iterations = more precision but more time

        Outputs: 
        A number between 0 and 1 indicating what percentage of hands lose to it (assume that half of the ties are losses and half are wins). 
        This is an estimate of the strength of the hand. 
    '''
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    strength = 0
    for _ in range(iters):
        deck = eval7.Deck()
        for card in hole_cards:
            deck.cards.remove(card)
        for card in board_cards:
            deck.cards.remove(card)
        deck.shuffle()
        opp_cards = deck.deal(2)

        # CHECK THIS
        curr_board_cards = board_cards.copy()
        while len(curr_board_cards) < 5:
            curr_board_cards.extend(deck.deal(1))
        
        my = eval7.evaluate(hole_cards + curr_board_cards)
        opp = eval7.evaluate(opp_cards + curr_board_cards)

        if my > opp:
            strength += 1
        elif my == opp:
            strength += 0.5

    return strength / iters

def compute_strength(hole, board=[]):
    '''
        Computes the exact number of hands that win, tie, and lose to your hand.
        
        Inputs: 
        hole (list of strings): A list of your two hole cards
        board (list of strings): A (possibly empty) list of the board cards
        iters (int): Number of iterations to run. More iterations = more precision but more time

        Outputs: 
        A 3-tuple (wins, ties, losses) indicating the percentage of wins, ties, and losses of this hand agaist all the other possible hands. 

        Note this function is really slow. Should really only be used after the river is shown. 
    '''
    
    hole_cards = [eval7.Card(card) for card in hole]
    board_cards = [eval7.Card(card) for card in board]
    deck=eval7.Deck()
    wins=0
    ties=0
    losses=0
    for card in hole_cards:
        deck.cards.remove(card)
    for card in board_cards:
        deck.cards.remove(card)
    for rest_of_board in combinations(deck, 5-len(board_cards)):
        for card in rest_of_board:
            deck.cards.remove(card)
        for opp_hole in combinations(deck, 2):
            my = eval7.evaluate(hole_cards + list(board_cards)+list(rest_of_board))
            opp = eval7.evaluate(list(opp_hole) + list(board_cards)+list(rest_of_board))
            if my>opp:
                wins+=1
            elif my==opp:
                ties+=1
            else:
                losses+=1
        for card in rest_of_board:
            deck.cards.append(card)
    return wins/(wins+ties+losses)

def mixed_strategy(legal_actions, my_pip, round_state, checkfold, checkcall, raise_amount=1):
    '''
        Does a randomized selection of actions depending on input probabilities

        Inputs: 
        legal actions: The set of legal actions
        my_pip: Your total contribution of chips this betting round
        round_state: Round state object from RoundState
        checkfold: The probability with which it will choose check-fold action
        checkcall: The probabiity with which it will choose check-call action
        1-checkfold-checkcall will be the probability of raising.
        raise_amount: How much it will raise given that it chooses raise. 

        Output: An action
    '''
    if random.random()<checkfold:
        return CheckFold(legal_actions)
    if random.random()<checkfold+checkcall:
        return CheckCall(legal_actions)
    return RaiseCheckCall(legal_actions, my_pip, round_state, raise_amount)

if __name__ == "__main__":
    print(estimate_strength(['Ah', 'As'], [], iters=50))
    print(estimate_strength(['Ah', 'As'], [], iters=100))
    print(estimate_strength(['Ah', 'As'], [], iters=200))
    print(estimate_strength(['Ah', 'As'], [], iters=500))
    print(estimate_strength(['Ah', 'As'], [], iters=1000))
    print(estimate_strength(['Ah', 'As'], [], iters=5000))
    
    #print(compute_strength(['Ah', 'As'], ['Ad', '2h', '5c', '6s', '6c']))