import os
import json
from collections import defaultdict, Counter

from tqdm import tqdm

NAME = "frijolbot"

def analyze_all_games(log_directory, bot_version="Frijol-4.1"):
    """
    Parse a folder of game logs where each file has exactly 1000 rounds of heads-up poker.
    Collect raw data for:
      - Games won/lost
      - Total pot size
      - Action counts (per street)
      - Positional action counts (SB vs. BB)
      - Combined data per street and per position
    """
    players = ["A", "B"]
    summary = {
        "total_games": 0,
        "games_won": 0,
        "games_lost": 0,
        "total_rounds": 0,
        "total_pot": 0,
        "street_action_counts": {
            "preflop": Counter(),
            "flop": Counter(),
            "turn": Counter(),
            "river": Counter()
        },
        "positional_action_counts": {
            "SB": Counter(),
            "BB": Counter()
        },
        "combined_counts": {
            "preflop": {
                "SB": Counter(),
                "BB": Counter()
            },
            "flop": {
                "SB": Counter(),
                "BB": Counter()
            },
            "turn": {
                "SB": Counter(),
                "BB": Counter()
            },
            "river": {
                "SB": Counter(),
                "BB": Counter()
            }
        }
    }

    for bot_player in players:
        # Process each game log
        for filename in os.listdir(log_directory):
            if not filename.endswith(".json"):
                continue

            player_a, player_b, bot, game_num = filename.split("||")
            game_num, _ = game_num.split(".")
            if bot != bot_version:
                continue
            if bot_player == "A" and player_a != NAME:
                continue
            if bot_player == "B" and player_b != NAME:
                continue
                
            filepath = os.path.join(log_directory, filename)
            with open(filepath, "r") as f:
                rounds = json.load(f)

            if not rounds:
                print("Malformed file:", filename)
                continue

            summary["total_games"] += 1
            summary["total_rounds"] += len(rounds)

            # Determine game winner
            final_round = rounds[-1]
            final_counts = final_round.get("winning_counts_end_round", {})
            bot_final = final_counts.get(bot_player, 0)
            opponent = "B" if bot_player == "A" else "A"
            opp_final = final_counts.get(opponent, 0)

            if bot_final > opp_final:
                summary["games_won"] += 1
            else:
                summary["games_lost"] += 1

            # Round-level data
            for rd in rounds:
                streets = rd.get("streets", [])
                if streets:
                    last_street = streets[-1]
                    summary["total_pot"] += last_street.get("pot_size_after_street", 0)

                for st in streets:
                    street_name = st.get("street_name", "").lower()
                    actions = st.get("actions", [])
                    for action_obj in actions:
                        player = action_obj.get("player")
                        action = action_obj.get("action", "").lower()
                        if player == bot_player:
                            summary["street_action_counts"][street_name][action] += 1

                blinds = rd.get("blinds", {})
                sb_player = blinds.get("small_blind", {}).get("player")
                position = "SB" if sb_player == bot_player else "BB"
                for st in streets:
                    street_name = st.get("street_name", "").lower()
                    actions = st.get("actions", [])
                    for action_obj in actions:
                        player = action_obj.get("player")
                        action = action_obj.get("action", "").lower()
                        if player == bot_player:
                            summary["positional_action_counts"][position][action] += 1
                            summary["combined_counts"][street_name][position][action] += 1

    # Convert Counters to dicts for JSON serialization
    summary["street_action_counts"] = {street: dict(counter) for street, counter in summary["street_action_counts"].items()}
    summary["positional_action_counts"] = {pos: dict(counter) for pos, counter in summary["positional_action_counts"].items()}
    summary["combined_counts"] = {street: {pos: dict(counter) for pos, counter in pos_dict.items()} for street, pos_dict in summary["combined_counts"].items()}

    return summary

def main():
    log_dir = "../data"  # Adjust to your directory of game files

    bot_versions = ["Frijol-1", "Frijol-2", "Frijol-2.1", "Frijol-3", "Frijol-3.1", "Frijol-3.2", "Frijol-4.0", "Frijol-4.1"]

    os.makedirs("../aggregate_data", exist_ok=True)

    for version in bot_versions:
        result = analyze_all_games(log_dir, bot_version=version)

        output_file = f"../aggregate_data/summary_{version}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()