from helper_bot import FrijolBot
import constants as constants
import utils as utils
import skeleton.states as states
from tqdm import tqdm
import csv
import numpy as np

def generate_hole_card_strengths(output_file, iterations=200):
    """
    Generates the strength for each pair of hole cards and outputs a CSV file.
    """
    rank_combinations = []

    # Generate all unique pairs of hole cards
    for i, rank1 in enumerate(constants.ranks):
        for rank2 in constants.ranks[i:]:
            for bounty in constants.ranks:
                if rank1 == rank2:
                    # Pairs (off suit, obviously)
                    rank_combinations.append((rank1 + "s", rank2 + "h", bounty))
                else:
                    # Suited combinations
                    rank_combinations.append((rank1 + "s", rank2 + "s", bounty))

                    # Offsuit combinations
                    rank_combinations.append((rank1 + "s", rank2 + "h", bounty))

    results = []
    for combo in tqdm(rank_combinations):
        # Evaluate the strength of each pair
        mock_bot = FrijolBot()
        mock_bot.active = 0
        mock_bot.opponent_bounty_distribution = np.ones(13) / 13

        mock_bot.round_state = states.RoundState
        mock_bot.round_state.hands = [combo[:2], []]
        mock_bot.round_state.deck = []
        mock_bot.round_state.street = 0
        mock_bot.round_state.bounties = [combo[2], None]

        strength = utils.estimate_hand_strength(mock_bot, bounty_strength=1, iterations=iterations)
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

if __name__ == "__main__":
    print("Generating hole card strengths...")
    generate_hole_card_strengths("hole_card_strengths.csv", iterations=200)