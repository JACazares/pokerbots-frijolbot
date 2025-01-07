import scipy.special
import math
import numpy as np
import eval7
from itertools import combinations

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


def monte_carlo_sim(hole, board=[], iters=5000):
    '''
    
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

        while str(curr_board_cards[-1])[1] == 'h' or str(curr_board_cards[-1])[1] == 'd':
            curr_board_cards.extend(deck.deal(1))
        
        my = eval7.evaluate(hole_cards + curr_board_cards)
        opp = eval7.evaluate(opp_cards + curr_board_cards)

        if my > opp:
            strength += 1
        elif my == opp:
            strength += 0.5

    return strength / iters

def compute_strength(hole, board=[]):
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
        print(board_cards)
        print(wins+ties+losses)
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
    print("wins: ", wins/(wins+ties+losses))
    print("ties: ", ties/(wins+ties+losses))
    print("losses: ", losses/(wins+ties+losses))
    print("total: ", wins+ties+losses)


if __name__ == "__main__":
    print(monte_carlo_sim(['Ah', 'As'], ['Ad', '2h', '5c', '6s']))
    #compute_strength(['Ah', 'As'], ['Ad', '2h', '5c', '6s', '6c'])