import random
import csv
import math
import numpy as np
import eval7
import scipy.special
from itertools import combinations
from tqdm import tqdm
from .skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction


def RaiseCheckCall(legal_actions, my_pip, round_state, raise_amount):
    if RaiseAction in legal_actions:
        min_raise, max_raise = (
            round_state.raise_bounds()
        )  # the smallest and largest numbers of chips for a legal bet/raise
        min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
        max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        raise_amount = min(raise_amount, max_raise)
        raise_amount = max(raise_amount, min_raise)
        print("I RAISE", raise_amount)
        return RaiseAction(raise_amount)
    return CheckCall(legal_actions)


def CheckFold(legal_actions):
    if CheckAction in legal_actions:
        print("I CHECK")
        return CheckAction()
    print("I FOLD")
    return FoldAction()


def CheckCall(legal_actions):
    if CheckAction in legal_actions:
        print("I CHECK")
        return CheckAction()
    print("I CALL")
    return CallAction()


def compute_checkfold_win_probability(rounds_left, bankroll, big_blind):
    """
    Computes the probability of winning by only checking or folding given a current bankroll and number of rounds left (including this one).

    Inputs:
    rounds_left: The number of rounds left to play, including this one.
    bankroll: Net wins or losses so far
    big_blind: True if you are the big blind, False otherwise

    Outputs:
    A number from 0 to 1 indicating the probability of winning with the check-fold strategy from now on.

    Note that this function can be used backwards, by inputting the negative bankroll and the negation of big_blind.
    This indicates the probability of you losing if the opponent does the check-fold strategy.
    """
    bounties_to_win = (
        math.ceil(
            (
                bankroll
                - 3 * rounds_left / 2
                - (rounds_left % 2) * (int(big_blind) - 0.5)
            )
            / 11
        )
        - 1
    )  # How many times the opponent can hit the bounty and you still win

    # Bring that number to rounds_left if it is too big. Of course. In that case the probability will just be 1
    bounties_to_win = min(bounties_to_win, rounds_left)

    # If it is negative, you have other problems
    bounties_to_win = max(bounties_to_win, 0)

    winning_cases = np.arange(bounties_to_win + 1)
    success_rate = 1 - 48 * 47 / (52 * 51)
    probabilities = np.array(
        [scipy.special.comb(rounds_left, case, exact=True) for case in winning_cases]
    )
    probabilities = (
        probabilities
        * (success_rate**winning_cases)
        * (1 - success_rate) ** (rounds_left - winning_cases)
    )
    return np.sum(probabilities)


def estimate_strength(
    hole,
    board=[],
    iters=200,
    my_bounty=None,
    bounty_strength=1,
    opp_bounty_distrib=[1 / 13] * 13,
):
    """
    Performs a Montecarlo search to approximate the strength of a hand.

    Inputs:
    hole (list of strings): A list of your two hole cards
    board (list of strings): A (possibly empty) list of the board cards
    iters (int): Number of iterations to run. More iterations = more precision but more time

    Outputs:
    A number between 0 and 1 indicating what percentage of hands lose to it (assume that half of the ties are losses and half are wins).
    This is an estimate of the strength of the hand.
    """

    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    strength = 0

    deck = eval7.Deck()
    for card in hole_cards:
        deck.cards.remove(card)
    for card in board_cards:
        deck.cards.remove(card)

    indices = np.arange(len(opp_bounty_distrib))  # List of indices (0 to 12)

    for _ in range(iters):
        next_cards = deck.sample(5 - len(board_cards) + 2)
        opp_cards = next_cards[:2]

        curr_board_cards = board_cards + next_cards[2:]

        my = eval7.evaluate(hole_cards + curr_board_cards)
        opp = eval7.evaluate(opp_cards + curr_board_cards)

        opp_bounty = random.choices(indices, weights=opp_bounty_distrib, k=1)[0]

        if my > opp:
            bounty_awarded = np.any(
                [my_bounty == eval7.ranks[card.rank] for card in hole_cards]
            ) or np.any(
                [my_bounty == eval7.ranks[card.rank] for card in curr_board_cards]
            )

            if bounty_awarded:
                strength += 1.25 * bounty_strength
            else:
                strength += 1
        elif my == opp:
            bounty_awarded = np.any(
                [my_bounty == eval7.ranks[card.rank] for card in hole_cards]
            ) or np.any(
                [my_bounty == eval7.ranks[card.rank] for card in curr_board_cards]
            )

            opp_bounty_awarded = np.any(
                [opp_bounty == card.rank for card in opp_cards]
            ) or np.any([opp_bounty == card.rank for card in curr_board_cards])

            if bounty_awarded and not opp_bounty_awarded:
                strength += 0.625
            elif not bounty_awarded and opp_bounty_awarded:
                strength += 0.375
            else:
                strength += 0.5
        else:
            opp_bounty_awarded = np.any(
                [opp_bounty == card.rank for card in opp_cards]
            ) or np.any([opp_bounty == card.rank for card in curr_board_cards])

            if opp_bounty_awarded:
                strength -= 0.25 * bounty_strength
            else:
                strength += 0

    return strength / iters


def generate_hole_card_strengths(output_file, iters=200):
    """
    Generates the strength for each pair of hole cards and outputs a CSV file.
    """

    suits = ["s", "h", "d", "c"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    rank_combinations = []
    bounties = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

    # Generate all unique pairs of hole cards
    for i, rank1 in enumerate(ranks):
        for j, rank2 in enumerate(ranks[i:], start=i):
            for bounty in bounties:
                if rank1 == rank2:
                    # Pairs (same rank)
                    rank_combinations.append(
                        (rank1 + "s", rank2 + "h", bounty)
                    )  # Arbitrary pair
                else:
                    # Suited combinations
                    rank_combinations.append((rank1 + "s", rank2 + "s", bounty))
                    # Offsuit combinations
                    rank_combinations.append(
                        (rank1 + "s", rank2 + "h", bounty)
                    )  # Arbitrary different suit pair

    # Evaluate the strength of each pair
    results = []
    for combo in tqdm(rank_combinations):
        strength = estimate_strength(combo[:2], iters=iters, my_bounty=combo[2])
        results.append(
            {"C1": combo[0], "C2": combo[1], "Bounty": combo[2], "Strength": strength}
        )

    # Sort by strength
    results.sort(key=lambda x: x["Strength"], reverse=True)

    # Write to CSV
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["C1", "C2", "Bounty", "Strength"])
        writer.writeheader()
        writer.writerows(results)

    print(f"CSV file '{output_file}' generated successfully!")


def compute_strength(hole, board=[]):
    """
    Computes the exact number of hands that win, tie, and lose to your hand.

    Inputs:
    hole (list of strings): A list of your two hole cards
    board (list of strings): A (possibly empty) list of the board cards
    iters (int): Number of iterations to run. More iterations = more precision but more time

    Outputs:
    A 3-tuple (wins, ties, losses) indicating the percentage of wins, ties, and losses of this hand agaist all the other possible hands.

    Note this function is really slow. Should really only be used after the river is shown.
    """

    hole_cards = [eval7.Card(card) for card in hole]
    board_cards = [eval7.Card(card) for card in board]
    deck = eval7.Deck()

    wins = 0
    ties = 0
    losses = 0

    for card in hole_cards:
        deck.cards.remove(card)

    for card in board_cards:
        deck.cards.remove(card)

    for cards_left in combinations(deck, 7 - len(board_cards)):
        opp_hole = list(cards_left)[:2]
        rest_of_board = list(cards_left)[2:]

        my = eval7.evaluate(hole_cards + board_cards + rest_of_board)
        opp = eval7.evaluate(opp_hole + board_cards + rest_of_board)

        if my > opp:
            wins += 1
        elif my == opp:
            ties += 1
        else:
            losses += 1

    return wins / (wins + ties + losses)


def mixed_strategy(
    legal_actions, my_pip, round_state, checkfold, checkcall, raise_amount=1
):
    """
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
    """

    random_var = random.random()

    if random_var < checkfold:
        return CheckFold(legal_actions)
    if random_var < checkfold + checkcall:
        return CheckCall(legal_actions)

    min_raise, _ = round_state.raise_bounds()
    std_dev = (raise_amount - min_raise) / 2
    raise_amount = int(np.random.normal(raise_amount, std_dev))

    return RaiseCheckCall(legal_actions, my_pip, round_state, raise_amount)


def compute_bounty_in_opponent_hole_cards_credence(numerator, len_board_cards):
    """
    
    """

    # TODO: this is probably slower than it should be.
    return 1 - scipy.special.comb(numerator - len_board_cards, 2, exact=True) / scipy.special.comb(50 - len_board_cards, 2, exact=True)


def compute_bounty_credences(distribution, hole_ranks, board_ranks):
    """
    Let B be the opponent's bounty, S be the union of the opponent's hole cards and the board cards. Compute
    $$P(B \in S | B = i)$$
    Distinguishing between
    i = board cards,
    i = both of my hole cards,
    i = one of my hole cards,
    i = any other card
    """

    # Partition ranks into each of the four cases
    board_ranks = np.array(board_ranks)
    hole_ranks = np.array([rank for rank in hole_ranks if rank not in board_ranks])
    remaining_ranks = np.array([rank for rank in range(13) if rank not in board_ranks and rank not in hole_ranks])

    # Check that all ranks are accounted for
    if not np.all( [ np.count_nonzero(board_ranks == rank)
            + np.count_nonzero(hole_ranks == rank)
            + np.count_nonzero(remaining_ranks == rank)
            == 1
            for rank in range(13)
        ]):
        raise ValueError("Ranks are not all accounted for")

    sum_board_card_probabilities = 0
    sum_opponent_hole_card_probabilities = 0
    probability_B_in_S_given_B_is_rank = np.zeros(13)

    for rank in board_ranks:
        probability_B_in_S_given_B_is_rank[rank] = 1
        sum_board_card_probabilities += distribution[rank]

    for rank in hole_ranks:
        probability_B_in_S_given_B_is_rank[rank] = (compute_bounty_in_opponent_hole_cards_credence(50 - (2 - len(hole_ranks) + 1), len(board_ranks)))
        sum_opponent_hole_card_probabilities += (distribution[rank] * probability_B_in_S_given_B_is_rank[rank])

    for rank in remaining_ranks:
        probability_B_in_S_given_B_is_rank[rank] = (compute_bounty_in_opponent_hole_cards_credence(50 - 4, len(board_ranks)))
        sum_opponent_hole_card_probabilities += (distribution[rank] * probability_B_in_S_given_B_is_rank[rank])

    return (
        sum_board_card_probabilities,
        sum_opponent_hole_card_probabilities,
        probability_B_in_S_given_B_is_rank,
    )


def update_opp_bounty_credences(
    distribution, bounty_awarded, street, hole=[], board=[], opp=[]
):
    """
    Updates opponent bounty probability distribution given the latest round result using bayesian inference

    Inputs:
    distribution: a list of size 13 with the probability distribution for each rank (0 to 12)
    bounty_awarded: a bool saying if opponent's bounty was awarded
    street: The street in which the round ended
    hole: my hole cards
    board: final board cards:
    opp: opponent cards (empty if not revealed)

    Output
    new_distribution: The updated distribution
    """
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    opp_cards = [eval7.Card(s) for s in opp]

    hole_ranks = [card.rank for card in hole_cards]
    board_ranks = [card.rank for card in board_cards]
    opponent_ranks = [card.rank for card in opp_cards]
    all_ranks = np.arange(13)

    new_distribution = np.zeros(13)

    (sum_board_card_probabilities,
     sum_opponent_hole_card_probabilities,
     probability_B_in_S_given_B_is_rank) =\
        compute_bounty_credences(distribution=distribution, hole_ranks=hole_ranks, board_ranks=board_ranks)

    # Opponent has visible cards
    if len(opp_cards) > 0:
        if bounty_awarded:
            for rank in all_ranks:
                if rank in board_ranks + opponent_ranks:
                    new_distribution[rank] = 0
                else:
                    new_distribution[rank] = distribution[rank]
        else:
            for rank in all_ranks:
                if rank in board_ranks + opponent_ranks:
                    new_distribution[rank] = distribution[rank]
                else:
                    new_distribution[rank] = 0

        # Renormalize new_distribution
        new_distribution = new_distribution / np.sum(new_distribution)

    # Opponent has no visible cards
    else:
        if bounty_awarded:
            for rank in all_ranks:
                new_distribution[rank] = (
                    probability_B_in_S_given_B_is_rank[rank]
                    * distribution[rank]
                    / (sum_board_card_probabilities + sum_opponent_hole_card_probabilities)
                )
        else:
            for rank in all_ranks:
                if rank in board_ranks:
                    new_distribution[rank] = 0
                else:
                    # TODO: Check this, it sounds wrong--
                    new_distribution[rank] = (
                        (1 - probability_B_in_S_given_B_is_rank[rank])
                        * distribution[rank]
                        / (1 - sum_board_card_probabilities - sum_opponent_hole_card_probabilities)
                    )

    return new_distribution


def compute_pot_odds(
    opp_pot,
    my_pot,
    hole,
    board,
    street,
    my_bounty_rank,
    opp_bounty_distribution=[1 / 13] * 13,
):
    """
    Computes pot odds using bounty

    Inputs:
    opp_pot: opponent contribution plus pip
    my_pot: my contribution plus pip
    hole: my hole cards
    board: the board cards
    my_bounty_rank: A string with my bounty rank


    Outputs:
    pot odds: Compare this number with the probability of winning
    """
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    if np.any(
        [my_bounty_rank == eval7.ranks[card.rank] for card in hole_cards + board_cards]
    ):
        R = 1  # Probability that my bounty is visible to me now (TODO: Change it to future)
    else:
        R = 0
    prob_bboard = 0  # After the for, it will be the sum of the probabilities of the board cards (distinct)
    prob_bHb = 0  # After the for, it will be the probability that B is in opp_hole and B is not in the board.
    prob_binS_gb_is_idx = [0] * 13
    for idx, prob in enumerate(opp_bounty_distribution):
        if np.any([idx == card.rank for card in board_cards]):
            prob_bboard += prob
            prob_binS_gb_is_idx[idx] = 1
        elif not np.any([idx == card.rank for card in hole_cards]):
            prob_binS_gb_is_idx[idx] = 1 - scipy.special.comb(
                46 - street, 2, exact=True
            ) / scipy.special.comb(50 - street, 2, exact=True)
            prob_bHb += prob * prob_binS_gb_is_idx[idx]
        elif np.all([idx == card.rank for card in hole_cards]):
            prob_binS_gb_is_idx[idx] = 1 - scipy.special.comb(
                48 - street, 2, exact=True
            ) / scipy.special.comb(50 - street, 2, exact=True)
            prob_bHb += prob * prob_binS_gb_is_idx[idx]
        else:
            prob_binS_gb_is_idx[idx] = 1 - scipy.special.comb(
                47 - street, 2, exact=True
            ) / scipy.special.comb(50 - street, 2, exact=True)
            prob_bHb += prob * prob_binS_gb_is_idx[idx]
    Q_now = (
        prob_bboard + prob_bHb
    )  # Probability that opponent's bounty is visible to them now
    Q_fut = Q_now  # TODO: Change it to future
    print("Q_now: ", Q_now)
    print("R: ", R)
    pot_odds = ((opp_pot + 20) * (Q_fut + 2) - (my_pot + 20) * (Q_now + 2)) / (
        (opp_pot + 20) * (Q_fut + 4 + R) - 80
    )
    return pot_odds


if __name__ == "__main__":
    # Run the script
    # print(estimate_strength(['7h', '2s'], iters=10000, bounty='2', bounty_strength=1, opp_bounty_distrib=[1/13]*13))
    # print(compute_checkfold_winprob(450, 927, True))

    # print(compute_strength(['Ah', 'As'], ['Ad', '2h', '5c', '6s', '6c']))
    opp_pot = 2
    my_pot = 1
    my_bounty_rank = "A"
    hole = ["3s", "Th"]
    board = []
    street = 0
    print((opp_pot - my_pot) / (2 * opp_pot))
    print(
        compute_pot_odds(
            opp_pot,
            my_pot,
            hole,
            board,
            street,
            my_bounty_rank,
            opp_bounty_distribution=[1 / 13] * 13,
        )
    )
