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
from io_utils import simplify_hole


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

    start_time = time.time()

    hole = bot.get_my_cards()
    board = bot.get_board_cards()
    opponent_bounty_distribution = bot.get_opponent_bounty_distribution()

    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]

    strength = 0

    deck = eval7.Deck()
    for card in hole_cards:
        deck.cards.remove(card)
    for card in board_cards:
        deck.cards.remove(card)

    for _ in range(iterations):
        montecarlo_next_cards = deck.sample(5 - len(board_cards) + 2)
        montecarlo_opponent_cards = montecarlo_next_cards[:2]
        montecarlo_board_cards = board_cards + montecarlo_next_cards[2:]

        montecarlo_my_strength = eval7.evaluate(hole_cards + montecarlo_board_cards)
        montecarlo_opponent_strength = eval7.evaluate(montecarlo_opponent_cards + montecarlo_board_cards)

        montecarlo_opponent_bounty = np.random.choice(13, p=opponent_bounty_distribution)

        montecarlo_my_bounty_awarded = np.any([montecarlo_opponent_bounty == card.rank for card in hole_cards]) or \
                                       np.any([montecarlo_opponent_bounty == card.rank for card in montecarlo_board_cards])

        montecarlo_opponent_bounty_awarded = np.any([montecarlo_opponent_bounty == card.rank for card in montecarlo_opponent_cards]) or \
                                             np.any([montecarlo_opponent_bounty == card.rank for card in montecarlo_board_cards])

        if montecarlo_my_strength > montecarlo_opponent_strength:
            strength += 1
            if montecarlo_my_bounty_awarded:
                strength += 0.25 * bounty_strength
        elif montecarlo_my_strength == montecarlo_opponent_strength:
            strength += 0.5
            if montecarlo_my_bounty_awarded and not montecarlo_opponent_bounty_awarded:
                strength += 0.125 * bounty_strength
            elif not montecarlo_my_bounty_awarded and montecarlo_opponent_bounty_awarded:
                strength += 0.125 * bounty_strength
        else:
            if montecarlo_opponent_bounty_awarded:
                strength -= 0.25 * bounty_strength
    
    print(f"Time elapsed: {time.time() - start_time}")

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

    updated_opponent_bounty_distribution = np.zeros(13)

    (sum_board_card_probabilities,
     sum_opponent_hole_card_probabilities,
     probability_B_in_S_given_B_is_rank) =\
        compute_bounty_credences(distribution=bot.get_opponent_bounty_distribution(), hole_ranks=hole_ranks, board_ranks=board_ranks)

    if len(opponent_cards) > 0 and bot.get_opponent_bounty_hit():
        # Set probability of all ranks that are not in the board or opponent's hole cards to 0 and renormalize
        for rank in constants.rank_index:
            if rank not in board_ranks + opponent_ranks:
                updated_opponent_bounty_distribution[rank] = 0
            else:
                updated_opponent_bounty_distribution[rank] = bot.get_opponent_bounty_distribution()[rank]

        updated_opponent_bounty_distribution = updated_opponent_bounty_distribution / np.sum(updated_opponent_bounty_distribution)

    elif len(opponent_cards) > 0 and not bot.get_opponent_bounty_hit():
        # Set probability of all ranks that are in the board or opponent's hole cards to 0 and renormalize
        # TODO: Add the small case where it's slightly less likely that their bounty is one of your hole cards

        for rank in constants.rank_index:
            if rank in board_ranks + opponent_ranks:
                updated_opponent_bounty_distribution[rank] = 0
            else:
                updated_opponent_bounty_distribution[rank] = bot.get_opponent_bounty_distribution()[rank]

        updated_opponent_bounty_distribution = updated_opponent_bounty_distribution / np.sum(updated_opponent_bounty_distribution)

    elif len(opponent_cards) == 0 and bot.get_opponent_bounty_hit():
        for rank in constants.rank_index:
            updated_opponent_bounty_distribution[rank] = probability_B_in_S_given_B_is_rank[rank] * bot.get_opponent_bounty_distribution()[rank] / (sum_board_card_probabilities + sum_opponent_hole_card_probabilities)

    elif len(opponent_cards) == 0 and not bot.get_opponent_bounty_hit():
        for rank in constants.rank_index:
            if rank in board_ranks:
                updated_opponent_bounty_distribution[rank] = 0
            else:
                # TODO: Check this, it sounds wrong--
                updated_opponent_bounty_distribution[rank] = (1 - probability_B_in_S_given_B_is_rank[rank]) * bot.get_opponent_bounty_distribution()[rank] / (1 - sum_board_card_probabilities - sum_opponent_hole_card_probabilities)

    return updated_opponent_bounty_distribution


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
    print("Q_now: ", Q_now)
    print("R: ", R)
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