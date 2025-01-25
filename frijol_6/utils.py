import random
import csv
import math
import numpy as np
import eval7
import scipy.special
from scipy.stats import binom
from itertools import combinations
from tqdm import tqdm
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import NUM_ROUNDS
from action_utils import CheckCall, CheckFold, RaiseCheckCall
from helper_bot import FrijolBot
import typing
import constants
import time
from io_utils import simplify_hole, expand_opponent_range


def compute_checkfold_win_probability(bot: FrijolBot):
    """
    Computes the probability of winning by only checking or folding given a current bankroll and number of rounds left (including this one).
    NOTE: This function can be used backwards, by inputting the negative bankroll and the negation of big_blind.
    This indicates the probability of you losing if the opponent does the check-fold strategy.

    Args:
        frijol_bot (FrijolBot): An instance of the FrijolBot class containing the current state of the game, including bankroll, round number, and big blind.

    Returns:
        probability (float): A number from 0 to 1 indicating the probability of winning with the check-fold strategy from now on.
    """
    bankroll = bot.get_bankroll()
    rounds_left = NUM_ROUNDS - bot.get_round_num() + 1
    big_blind = bot.get_big_blind()

    # How many times the opponent can hit the bounty and you still win?
    bounties_to_win = math.ceil((bankroll - 3*rounds_left/2 - (rounds_left % 2) * (int(big_blind) - 0.5)) / 11) - 1 
    bounties_to_win = min(bounties_to_win, rounds_left)
    bounties_to_win = max(bounties_to_win, 0)

    success_rate = 1 - 48*47/(52*51)
    return binom.cdf(bounties_to_win, rounds_left, success_rate)


def estimate_hand_strength(bot: FrijolBot, bounty_strength: float = 1.0, iterations: int = 200):
    """
    Performs a Monte Carlo search to approximate the strength of a hand.

    Parameters:
        bot (FrijolBot): The bot instance containing the current hand and board state.
        bounty_strength (float): The strength of the bounty. This is a multiplier on how much
            the bounty affects the returns of the hand.
            A value of 1.0 indicates that pots where the bounty is awarded are always large
            (so the +10 is not significant), while a value of 11.5 indicates that pots where
            the bounty is awarded are always small (so the +10 is significant).
        iterations (int): The number of Monte Carlo iterations to perform (default is 2000).

    Returns:
        strength (float): A number between 0 and 1 indicating the estimated strength of the hand. 
            This represents the percentage of hands that lose to the current hand, 
            assuming that half of the ties are losses and half are wins.
    """

    hole = bot.get_my_cards()
    board = bot.get_board_cards()
    # opponent_bounty_distribution = bot.get_opponent_bounty_distribution()
    opponent_range = np.triu(bot.get_opponent_range())
    flat_opponent_range = opponent_range.flatten()
    probabilities = flat_opponent_range / np.sum(flat_opponent_range)

    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]

    strength = 0
    deck = eval7.Deck()
    for card in hole_cards:
        deck.cards.remove(card)
    for card in board_cards:
        deck.cards.remove(card)

    for _ in range(iterations):
        random_opponent_cards_index = np.random.choice(len(probabilities), p=probabilities)
        random_opponent_cards_tuple = np.unravel_index(random_opponent_cards_index, opponent_range.shape)
        montecarlo_opponent_cards = list(map(lambda x : eval7.Deck()[-x - 1], random_opponent_cards_tuple))

        for card in montecarlo_opponent_cards:
            deck.cards.remove(card)
        montecarlo_board_cards = board_cards + deck.sample(5 - len(board_cards))
        for card in montecarlo_opponent_cards:
            deck.cards.append(card)
        
        montecarlo_my_strength = eval7.evaluate(hole_cards + montecarlo_board_cards)
        montecarlo_opponent_strength = eval7.evaluate(montecarlo_opponent_cards + montecarlo_board_cards)

        # montecarlo_opponent_bounty = np.random.choice(13, p=opponent_bounty_distribution)

        # montecarlo_my_bounty_awarded = np.any([montecarlo_opponent_bounty == card.rank for card in hole_cards]) or \
        #                                np.any([montecarlo_opponent_bounty == card.rank for card in montecarlo_board_cards])

        # montecarlo_opponent_bounty_awarded = np.any([montecarlo_opponent_bounty == card.rank for card in montecarlo_opponent_cards]) or \
        #                                      np.any([montecarlo_opponent_bounty == card.rank for card in montecarlo_board_cards])

        if montecarlo_my_strength > montecarlo_opponent_strength:
            strength += 1
            # if montecarlo_my_bounty_awarded:
            #     strength += 0.25 * bounty_strength
        elif montecarlo_my_strength == montecarlo_opponent_strength:
            strength += 0.5
            # if montecarlo_my_bounty_awarded and not montecarlo_opponent_bounty_awarded:
            #     strength += 0.125 * bounty_strength
            # elif not montecarlo_my_bounty_awarded and montecarlo_opponent_bounty_awarded:
            #     strength += 0.125 * bounty_strength
        else:
            strength += 0
            # if montecarlo_opponent_bounty_awarded:
            #     strength -= 0.25 * bounty_strength
    
    return strength / iterations


def compute_exact_hand_strength(bot: FrijolBot):
    """
    This function evaluates the strength of the bot's hand by comparing it against all possible opponent hands
    given the current board state. It simulates the remaining cards and determines the win, tie, and loss ratios.

    This function does not take into account neither your nor the opponent's bounty.

    NOTE: This function is computationally expensive and should only be used after the river is shown.

    Args:
        bot (FrijolBot): The bot instance containing the hole cards and board state.
    Returns:
        strength (float): The win ratio of the bot's hand.
    """

    hole = bot.get_my_cards()
    board = bot.get_board_cards()

    hole_cards = [eval7.Card(card) for card in hole]
    board_cards = [eval7.Card(card) for card in board]
    deck = eval7.Deck()
    for card in hole_cards:
        deck.cards.remove(card)
    for card in board_cards:
        deck.cards.remove(card)

    wins = 0
    ties = 0
    losses = 0

    for cards_left in combinations(deck, 7 - len(board_cards)):
        simulated_opponent_hole_cards = list(cards_left)[:2]
        simulated_board_cards = board_cards + list(cards_left)[2:]

        simulated_my_strength = eval7.evaluate(hole_cards + simulated_board_cards)
        simulated_opponent_strength = eval7.evaluate(simulated_opponent_hole_cards + simulated_board_cards)

        if simulated_my_strength > simulated_opponent_strength:
            wins += 1
        elif simulated_my_strength == simulated_opponent_strength:
            ties += 1
        else:
            losses += 1

    return wins / (wins + ties + losses)


# TODO: Revise this whole function. WRITE A LOT OF TESTS
def compute_bounty_credences(distribution, hole_ranks, board_ranks):
    """
    Compute the probability the opponent's bounty is present in their hole cards or the board cards.

    Let B be the opponent's bounty, S be the union of the opponent's hole cards and the board cards. Compute
    $$P(B \in S | B = i)$$

    Distinguishing between
    i = board cards,
    i = both of my hole cards,
    i = one of my hole cards,
    i = any other card

    """

    def compute_bounty_in_opponent_hole_cards_credence(numerator, len_board_cards):
        """
        Compute the probability that opponent has a bounty in their hole cards?
        """

        # TODO: this is probably slower than it should be.
        return 1 - scipy.special.comb(numerator - len_board_cards, 2, exact=True) / scipy.special.comb(50 - len_board_cards, 2, exact=True)

    # Partition ranks into each of the four cases
    sum_board_card_probabilities = 0
    sum_opponent_hole_card_probabilities = 0
    probability_B_in_S_given_B_is_rank = np.zeros(13)

    for rank in constants.rank_index:
        if rank in board_ranks:
            probability_B_in_S_given_B_is_rank[rank] = 1
            sum_board_card_probabilities += distribution[rank]
        elif rank in hole_ranks:
            if hole_ranks[0] == hole_ranks[1]:
                off_limits = 4
            else:
                off_limits = 5

            probability_B_in_S_given_B_is_rank[rank] = compute_bounty_in_opponent_hole_cards_credence(52 - off_limits, len(board_ranks))
            sum_opponent_hole_card_probabilities += (distribution[rank] * probability_B_in_S_given_B_is_rank[rank])
        else:
            probability_B_in_S_given_B_is_rank[rank] = (compute_bounty_in_opponent_hole_cards_credence(52 - 2 - 4, len(board_ranks)))
            sum_opponent_hole_card_probabilities += (distribution[rank] * probability_B_in_S_given_B_is_rank[rank])

    return (
        sum_board_card_probabilities,
        sum_opponent_hole_card_probabilities,
        probability_B_in_S_given_B_is_rank,
    )


def update_opponent_bounty_credences(bot: FrijolBot):
    """
    Updates opponent bounty probability distribution given the latest round result using Bayesian inference.

    Parameters:
        bot (FrijolBot): The bot instance containing the current game state and opponent information.

    Returns:
        new_opponent_bounty_distribution (np.ndarray): The updated probability distribution of opponent's bounty credences.
    """

    hole = bot.get_my_cards()
    board = bot.get_board_cards()
    opponent = bot.get_opponent_cards()

    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    opponent_cards = [eval7.Card(s) for s in opponent]

    hole_ranks = [card.rank for card in hole_cards]
    board_ranks = [card.rank for card in board_cards]
    opponent_ranks = [card.rank for card in opponent_cards]

    distribution = bot.get_opponent_bounty_distribution()
    street = bot.get_street()
    bounty_awarded = bot.get_opponent_bounty_hit()
    new_distribution = np.zeros(13)

    prob_bboard=0 #After the for, it will be the sum of the probabilities of the board cards (distinct)
    prob_bHb=0 #After the for, it will be the probability that B is in opp_hole and B is not in the board.
    prob_binS_gb_is_idx=[0]*13
    for idx, prob in enumerate(distribution):
            if np.any([idx == card.rank for card in board_cards]):
                prob_bboard+=prob
                prob_binS_gb_is_idx[idx]=1
            elif not np.any([idx == card.rank for card in hole_cards]):
                prob_binS_gb_is_idx[idx]=(1-scipy.special.comb(46-street, 2, exact=True)/scipy.special.comb(50-street, 2, exact=True))
                prob_bHb+=prob*prob_binS_gb_is_idx[idx]
            elif np.all([idx == card.rank for card in hole_cards]):
                prob_binS_gb_is_idx[idx]=(1-scipy.special.comb(48-street, 2, exact=True)/scipy.special.comb(50-street, 2, exact=True))
                prob_bHb+=prob*prob_binS_gb_is_idx[idx]
            else:
                prob_binS_gb_is_idx[idx]=(1-scipy.special.comb(47-street, 2, exact=True)/scipy.special.comb(50-street, 2, exact=True))
                prob_bHb+=prob*prob_binS_gb_is_idx[idx]           
    if bounty_awarded and len(opponent_cards)==0: #Bounty was awarded and opponent has no cards visible
        for idx, prob in enumerate(distribution):
            new_distribution[idx]=prob_binS_gb_is_idx[idx]*prob/(prob_bboard+prob_bHb) #Bayes rule
    elif bounty_awarded and len(opponent_cards)>0: #bounty awarded and opponent has visible cards
        prob_sum=0
        for idx, prob in enumerate(distribution):
            if idx not in [card.rank for card in board_cards+opponent_cards]:
                prob_sum+=distribution[idx]
                new_distribution[idx]=0
        for idx, prob in enumerate(distribution):
            if idx in [card.rank for card in board_cards+opponent_cards]:
                new_distribution[idx]=prob/(1-prob_sum)
    elif not bounty_awarded and len(opponent_cards)==0: #Bounty not awarded and opponent has no visible cards
        prob_sum=0
        for idx, prob in enumerate(distribution):
            if idx in [card.rank for card in board_cards]:
                prob_sum+=distribution[idx]
                new_distribution[idx]=0
        for idx, prob in enumerate(distribution):
            if idx not in [card.rank for card in board_cards]:
                new_distribution[idx]=(1-prob_binS_gb_is_idx[idx])*prob/(1-prob_bboard-prob_bHb)
    else: #Bounty not awarded and opponent has visible cards
        prob_sum=0
        for idx, prob in enumerate(distribution):
            if idx in [card.rank for card in board_cards+opponent_cards]:
                prob_sum+=distribution[idx]
                new_distribution[idx]=0
        for idx, prob in enumerate(distribution):
            if idx not in [card.rank for card in board_cards+opponent_cards]:
                new_distribution[idx]=prob/(1-prob_sum)
    return new_distribution

def compute_pot_odds(bot: FrijolBot):
    """
    Computes the pot odds using the bounty system.

    Parameters:
        bot (FrijolBot): The bot instance containing the current game state, including the pot contributions, hole cards, and board cards.

    Returns:
        pot_odds (float): The computed pot odds, which can be compared with the probability of winning.
            The function calculates the pot odds by considering the bot's and opponent's contributions to the pot, 
            the bot's bounty rank, and the opponent's bounty distribution. It evaluates the visibility of the bounties 
            on the board and in the hole cards, and uses combinatorial calculations to estimate the probabilities 
            involved in the pot odds formula.
    """
    hole = bot.get_my_cards()
    board = bot.get_board_cards()
    street = bot.get_street()

    opponent_pot = bot.get_opponent_contribution()
    my_pot = bot.get_my_contribution()

    my_bounty_rank = bot.get_my_bounty()
    opponent_bounty_distribution = bot.get_opponent_bounty_distribution()

    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]

    hole_ranks = [card.rank for card in hole_cards]
    board_ranks = [card.rank for card in board_cards]

    if np.any([my_bounty_rank == eval7.ranks[card.rank] for card in hole_cards + board_cards]):
        R = 1  # Probability that my bounty is visible to me now (TODO: Change it to future)
    else:
        R = 0
    
    (sum_board_card_probabilities,
     sum_opponent_hole_card_probabilities,
     probability_B_in_S_given_B_is_rank) =\
        compute_bounty_credences(distribution=opponent_bounty_distribution, hole_ranks=hole_ranks, board_ranks=board_ranks)

    Q_now = sum_board_card_probabilities + sum_opponent_hole_card_probabilities  # Probability that opponent's bounty is visible to them now

    Q_fut = Q_now  # TODO: Change it to future
    # print("Q_now: ", Q_now)
    # print("R: ", R)
    pot_odds = ((opponent_pot + 20) * (Q_fut + 2) - (my_pot + 20) * (Q_now + 2)) / (
        (opponent_pot + 20) * (Q_fut + 4 + R) - 80)
    return pot_odds


def preflop_action_distribution(bot: FrijolBot, call_range_matrix: np.array, raise_range_matrix: np.array):
    hole = bot.get_my_cards()
    my_bounty=bot.get_my_bounty()
    opponent_bounty_distribution = bot.get_opponent_bounty_distribution()

    hole_cards = [eval7.Card(s) for s in hole]
    row, column=simplify_hole(hole)
    if np.any([my_bounty == card.rank for card in hole_cards]):
        row=row+13

    call_probability = call_range_matrix[row][column]
    raise_probability = raise_range_matrix[row][column]
    fold_probability = 1-call_probability-raise_probability
    
    return fold_probability, call_probability, raise_probability

def update_opponent_range(bot: FrijolBot):

    hole=bot.get_my_cards()
    board=bot.get_board_cards()
    hole_cards=[eval7.Card(s) for s in hole]
    board_cards=[eval7.Card(s) for s in board]
    probability_of_opp_action_given_opp_hand = np.zeros([52, 52])

    current_opponent_range=bot.get_opponent_range()
    updated_opponent_range=bot.get_opponent_range()

    expanded_BB_3bet_range_vs_open = expand_opponent_range(bot.BB_3bet_range_vs_open[:, 0:13])
    expanded_BTN_opening_range = expand_opponent_range(bot.BTN_opening_range[:, 0:13])
    expanded_BTN_4bet_range_vs_3bet = expand_opponent_range(bot.BTN_4bet_range_vs_3bet[:, 0:13])
    expanded_BB_call_range_vs_open = expand_opponent_range(bot.BB_call_range_vs_open[:, 0:13])
    expanded_BB_call_range_vs_4bet = expand_opponent_range(bot.BB_call_range_vs_4bet[:, 0:13])
    expanded_BTN_call_range_vs_3bet = expand_opponent_range(bot.BTN_call_range_vs_3bet[:, 0:13])
    ones = np.ones((52, 52))

    street = bot.get_street()
    big_blind = bot.get_big_blind()
    my_contribution = bot.get_my_contribution()
    my_pip = bot.get_my_pip()
    opp_pip = bot.get_opponent_pip()
    my_contribution = bot.get_my_contribution()

    #start_time = time.time()

    if street==0:
        if not big_blind:
            if not my_pip==1: #Opponent 3betted 
                probability_of_opp_action_given_opp_hand = expanded_BB_3bet_range_vs_open
            else: #opponent has done nothing yet
                probability_of_opp_action_given_opp_hand = ones
        else: 
            if my_pip==2 and opp_pip ==1: #nothing has happened
                probability_of_opp_action_given_opp_hand = ones
            elif my_pip==2 and opp_pip==2: # opp LIMPED
                probability_of_opp_action_given_opp_hand = expanded_BTN_opening_range
            elif my_pip==2 and opp_pip<40: # opp opened
                probability_of_opp_action_given_opp_hand = expanded_BTN_opening_range
            else: #opp 4-betted
                probability_of_opp_action_given_opp_hand = expanded_BTN_4bet_range_vs_3bet
    elif street==3 and bot.opponent_called:
        if not big_blind:
            if my_contribution<10:
                probability_of_opp_action_given_opp_hand = expanded_BB_call_range_vs_open
            else:
                probability_of_opp_action_given_opp_hand = expanded_BB_call_range_vs_4bet
        else:
            probability_of_opp_action_given_opp_hand = expanded_BTN_call_range_vs_3bet
    else:
        probability_of_opp_action_given_opp_hand = ones

    # Zero all hands that include any of the cards in the hole or board
    for idx in range(52):
        if np.any([eval7.Deck()[51-idx] == card for card in hole_cards + board_cards]):
            probability_of_opp_action_given_opp_hand[idx, :]=0
            probability_of_opp_action_given_opp_hand[:, idx]=0
    

    probability_of_opp_action = np.sum(np.triu(probability_of_opp_action_given_opp_hand * current_opponent_range))
    updated_opponent_range = np.triu(probability_of_opp_action_given_opp_hand * current_opponent_range / probability_of_opp_action)

    return updated_opponent_range

def update_opponent_actions(bot: FrijolBot):
    big_blind = bot.get_big_blind()
    my_pip = bot.get_my_pip()
    opp_pip = bot.get_opponent_pip()
    street = bot.get_street()
    previous_street = bot.get_previous_street()

    if big_blind:
        if street == 0:
            if len(bot.opponent_actions) == 0:
                bot.opponent_actions.append(("Post Blind", 1))

            if opp_pip == my_pip:
                bot.opponent_actions.append(("Call",))
            elif opp_pip > my_pip:
                bot.opponent_actions.append(("Raise", opp_pip))
        else:
            if previous_street != street:
                if bot.previously_raised:
                    bot.opponent_actions.append(("Call",))
                else:
                    bot.opponent_actions.append(("Check",))
            else:
                bot.opponent_actions.append(("Raise", opp_pip))
    else:
        if street == 0:
            if opp_pip == 2:
                bot.opponent_actions.append(("Post Blind", 2))
            else:
                bot.opponent_actions.append(("Raise", opp_pip))
        else:
            if previous_street != street:
                if bot.previously_raised:
                    bot.opponent_actions.append(("Call",))
                
                if opp_pip == 0:
                    bot.opponent_actions.append(("Check",))
                else:
                    bot.opponent_actions.append(("Raise", opp_pip))
            else:
                bot.opponent_actions.append(("Raise", opp_pip))

    bot.previously_raised = False