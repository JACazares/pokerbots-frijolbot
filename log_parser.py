import json
import re


def parse_pokerbots_log_to_json(filepath):
    """
    Reads a text file representing a series of rounds in your Pokerbots game
    and returns a list of dictionaries, each representing a round in a structured format.
    """

    rounds = []
    current_round = None
    street_actions = []

    global_bounty = {"A": None, "B": None}

    # We'll track which street we're in (preflop, flop, turn, river).
    # Since the text lumps them together, we might guess based on triggers like "Flop [cards], Turn [cards], River [cards]".
    current_street = "preflop"

    # Some regex patterns we may use
    round_header_pattern = re.compile(
        r"^Round\s+#(\d+),\s+(A|B)\s+\((-?\d+)\),\s+(A|B)\s+\((-?\d+)\)$"
    )
    bounty_reset_pattern = re.compile(
        r"^Bounties reset to ([2-9TAJQK]+) for player (A|B) and ([2-9TAJQK]+) for player (A|B)$"
    )
    blind_pattern = re.compile(r"^(A|B) posts the blind of (\d+)$")
    dealt_pattern = re.compile(
        r"^(A|B) dealt \[([2-9TJQKA][cdhs])\s+([2-9TJQKA][cdhs])\]$"
    )
    action_pattern = re.compile(
        r"^(A|B)\s+(folds|calls|checks|bets\s+\d+|raises to\s+\d+)$"
    )
    awarded_pattern = re.compile(r"^(A|B)\s+awarded\s+(-?\d+)$")
    winning_pattern = re.compile(
        r"^Winning counts at the end of the round:\s+,\s+(A|B)\s+\((-?\d+)\),\s+(A|B)\s+\((-?\d+)\)$"
    )
    flop_turn_river_pattern = re.compile(
        r"^(Flop|Turn|River)\s+\[(.+)\],\s+(A|B)\s+\(\d+\),\s+(A|B)\s+\(\d+\)$"
    )
    stacks_pattern = re.compile(r"^Current stacks:\s+(\d+),\s+(\d+)$")

    # Helper to finalize a street segment
    def finalize_street():
        street_actions = []
        # """Adds the collected actions for the current street to the round data."""
        # if current_round and street_actions:
        #     # Add the current street to 'streets'
        #     current_round["streets"].append({
        #         "street_name": current_street,
        #         "actions": street_actions.copy()
        #     })

    with open(filepath, "r") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # 1. Check if this line starts a new round
            match_round_header = round_header_pattern.match(line)
            if match_round_header:
                # If we already had a current round in progress, we finalize it
                if current_round:
                    # finalize any leftover street actions
                    finalize_street()
                    rounds.append(current_round)

                round_number = int(match_round_header.group(1))
                score = {}
                score[match_round_header.group(2)] = int(
                    match_round_header.group(3)
                )  # Not always net? It's what's in parentheses
                score[match_round_header.group(4)] = int(
                    match_round_header.group(5)
                )  # Not always net? It's what's in parentheses

                # Start a new round structure
                current_round = {
                    "round_number": round_number,
                    "score_at_start": {"A": score["A"], "B": score["B"]},
                    "bounties": {"A": global_bounty["A"], "B": global_bounty["B"]},
                    "players": {"A": {"hole_cards": None}, "B": {"hole_cards": None}},
                    "blinds": {},
                    "streets": [],
                    "awards": {"A": 0, "B": 0},
                    "winning_counts_end_round": {"A": None, "B": None},
                }
                # Reset for the new round
                street_actions = []
                current_street = "preflop"

                current_round["streets"].append(
                    {
                        "street_name": current_street,
                        "community_cards": [],
                        "actions": street_actions,
                    }
                )

                continue

            # 2. Bounty reset line
            match_bounty = bounty_reset_pattern.match(line)
            if match_bounty and current_round:
                global_bounty[match_bounty.group(2)] = match_bounty.group(1)
                global_bounty[match_bounty.group(4)] = match_bounty.group(3)
                current_round["bounties"][match_bounty.group(2)] = match_bounty.group(1)
                current_round["bounties"][match_bounty.group(4)] = match_bounty.group(3)
                continue

            # 3. Blind posting
            match_blind = blind_pattern.match(line)
            if match_blind and current_round:
                player = match_blind.group(1)
                amount = int(match_blind.group(2))
                if "small_blind" not in current_round["blinds"]:
                    current_round["blinds"]["small_blind"] = {
                        "player": player,
                        "amount": amount,
                    }
                else:
                    current_round["blinds"]["big_blind"] = {
                        "player": player,
                        "amount": amount,
                    }
                # Record as an action in preflop
                street_actions.append(
                    {"player": player, "action": "post_blind", "amount": amount}
                )
                continue

            # 4. Cards dealt
            match_dealt = dealt_pattern.match(line)
            if match_dealt and current_round:
                player = match_dealt.group(1)
                card1 = match_dealt.group(2)
                card2 = match_dealt.group(3)
                current_round["players"][player]["hole_cards"] = [card1, card2]
                continue

            # 5. Action line
            match_action = action_pattern.match(line)
            if match_action and current_round:
                player = match_action.group(1)
                raw_action = match_action.group(2)

                # parse bet amount if "raises to X"
                if raw_action.startswith("raises to"):
                    # e.g. "raises to 10"
                    # we capture the numeric
                    raise_amount_str = raw_action.split("raises to")[-1].strip()
                    raise_amount = int(raise_amount_str)
                    street_actions.append(
                        {"player": player, "action": "raise", "amount": raise_amount}
                    )
                elif raw_action == "calls":
                    street_actions.append(
                        {
                            "player": player,
                            "action": "call",
                            "amount": None,  # we don't have the direct call size here
                        }
                    )
                elif raw_action == "checks":
                    street_actions.append(
                        {"player": player, "action": "check", "amount": 0}
                    )
                elif raw_action == "folds":
                    street_actions.append(
                        {"player": player, "action": "fold", "amount": 0}
                    )
                elif raw_action.startswith("bets"):
                    # e.g. "bets 2"
                    bet_amount_str = raw_action.split("bets")[-1].strip()
                    bet_amount = int(bet_amount_str)
                    street_actions.append(
                        {"player": player, "action": "bet", "amount": bet_amount}
                    )
                continue

            # 6. Flop / Turn / River indicator
            match_ftr = flop_turn_river_pattern.match(line)
            if match_ftr and current_round:
                # finalize the previous street first
                finalize_street()

                street_keyword = match_ftr.group(1).lower()  # 'Flop', 'Turn', 'River'
                card_string = match_ftr.group(2)  # e.g. "Jh Td Js"
                # parse the cards as a list
                community_cards = [c.strip() for c in card_string.split()]

                current_street = street_keyword
                street_actions = []  # start collecting for next street

                # Add an initial street object
                current_round["streets"].append(
                    {
                        "street_name": current_street,
                        "community_cards": community_cards,
                        "actions": street_actions,
                    }
                )
                # We'll fill "actions" once we parse them, but we might overwrite or merge
                # the existing object in finalize_street if we keep consistent references.
                continue

            # 7. Current stacks line (optional, you might store it or not)
            match_stacks = stacks_pattern.match(line)
            if match_stacks and current_round:
                # If you want to store these per-street, you can do so
                # For brevity, we ignore it in the final JSON here,
                # but you might want to store inside each street.
                # stack_a = int(match_stacks.group(1))
                # stack_b = int(match_stacks.group(2))
                continue

            # 8. Awarded pattern (net changes)
            match_awarded = awarded_pattern.match(line)
            if match_awarded and current_round:
                player = match_awarded.group(1)
                amount = int(match_awarded.group(2))
                # This is the net amount for that player
                current_round["awards"][player] += amount
                continue

            # 9. End of round winning counts
            match_winning = winning_pattern.match(line)
            if match_winning and current_round:
                final = {}
                final[match_winning.group(1)] = int(match_winning.group(2))
                final[match_winning.group(3)] = int(match_winning.group(4))
                current_round["winning_counts_end_round"]["A"] = final["A"]
                current_round["winning_counts_end_round"]["B"] = final["B"]
                # We'll finalize after reading this, but sometimes there's overlap with next round's start
                continue

        # End of file: if there's a round in progress, finalize it
        if current_round:
            finalize_street()
            rounds.append(current_round)

    return rounds


def main():
    filepath = "gamelog.txt"  # Replace with your actual file path
    rounds_data = parse_pokerbots_log_to_json(filepath)

    # Convert to JSON string (pretty-printed for demonstration)
    json_output = json.dumps(rounds_data, indent=2)
    with open("gamelog.json", "w") as outfile:
        outfile.write(json_output)


if __name__ == "__main__":
    main()
