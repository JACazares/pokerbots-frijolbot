import eval7
import itertools
import numpy as np

def estimate_hand_strength(hole, board, opponent_bounty_distribution, my_bounty_rank, bounty_strength: float = 1.0, iterations: int = 200):
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

        montecarlo_my_bounty_awarded = np.any([my_bounty_rank == card.rank for card in hole_cards]) or \
                                       np.any([my_bounty_rank == card.rank for card in montecarlo_board_cards])

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
    
    return strength / iterations

def main():
    deck = list(map(str, eval7.Deck()))

    print("{" + "\",\"".join(deck), "}")

    hand_strengths = {}
    from tqdm import tqdm
    for cards in tqdm(list(itertools.combinations(deck, 5))):
        for my_bounty_rank in range(13):
            strength = estimate_hand_strength(hole=cards[:2],
                                              board=cards[2:],
                                              my_bounty_rank=my_bounty_rank,
                                              opponent_bounty_distribution=np.ones(13)/13,
                                              iterations=200)
            hand_strengths[(my_bounty_rank, *cards)] = strength
    
    
if __name__ == "__main__":
    main()