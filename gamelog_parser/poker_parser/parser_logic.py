import re
from dataclasses import asdict
from poker_parser.structures import RoundData, Street, Showdown


class PokerLogParser:
    """
    A class-based parser that processes heads-up Hold'em logs line by line.
    Each handle_XXX method is focused on one regex/pattern.
    """

    def __init__(self):
        # Storage for final results
        self.rounds = []
        self.current_round = None

        # Round-level tracking
        self.pot = 0
        self.player_stacks = {"A": 400, "B": 400}
        self.player_contributions = {"A": 0, "B": 0}
        self.bounty = {"A": None, "B": None}

        # Regex definitions
        self.round_header_pattern = re.compile(
            r"^Round\s+#(\d+),\s+(A|B)\s+\((-?\d+)\),\s+(A|B)\s+\((-?\d+)\)$"
        )
        self.bounty_reset_pattern = re.compile(
            r"^Bounties reset to ([2-9TJQKA]) for player (A|B) and ([2-9TJQKA]) for player (A|B)$"
        )
        self.blind_pattern = re.compile(r"^(A|B) posts the blind of (\d+)$")
        self.dealt_pattern = re.compile(
            r"^(A|B) dealt \[([2-9TJQKA][cdhs])\s+([2-9TJQKA][cdhs])\]$"
        )
        self.action_pattern = re.compile(
            r"^(A|B)\s+(folds|calls|checks|bets\s+\d+|raises to\s+\d+)$"
        )
        self.awarded_pattern = re.compile(r"^(A|B)\s+awarded\s+(-?\d+)$")
        self.winning_pattern = re.compile(
            r"^Winning counts at the end of the round:\s+,\s+(A|B)\s+\((-?\d+)\),\s+(A|B)\s+\((-?\d+)\)$"
        )
        self.flop_turn_river_pattern = re.compile(
            r"^(Flop|Turn|River)\s+\[(.+)\],\s+(A|B)\s+\(\d+\),\s+(A|B)\s+\(\d+\)$"
        )
        self.stacks_pattern = re.compile(r"^Current stacks:\s+(\d+),\s+(\d+)$")
        self.shows_pattern = re.compile(
            r"^(A|B)\s+shows\s+\[([2-9TJQKA][cdhs])\s+([2-9TJQKA][cdhs])\]$"
        )

    def parse_file(self, filepath: str):
        """
        Main entry point to parse an entire file.
        Reads line by line, calls parse_line(), and returns a list of dictionaries suitable for JSON.
        """
        with open(filepath, "r") as infile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                self.parse_line(line)

        # Finalize any in-progress round
        self.finalize_current_round()

        # Convert to dicts (so it's JSON-serializable)
        return [asdict(r) for r in self.rounds]

    def parse_string(self, log_text: str):
        """
        Allows testing with a string-based log
        rather than reading from a file.
        """
        for line in log_text.splitlines():
            line = line.strip()
            if not line:
                continue
            self.parse_line(line)
        self.finalize_current_round()
        return [asdict(r) for r in self.rounds]

    def parse_line(self, line: str):
        """
        Tries each 'handle_' method in turn. If a pattern matches, returns early.
        """
        # The order here matters: check from the most specific to the most general
        if self.handle_round_header(line):
            return
        if self.handle_bounty_reset(line):
            return
        if self.handle_blind(line):
            return
        if self.handle_dealt_cards(line):
            return
        if self.handle_action(line):
            return
        if self.handle_flop_turn_river(line):
            return
        if self.handle_stacks_line(line):
            return
        if self.handle_shows_line(line):
            return
        if self.handle_awarded(line):
            return
        if self.handle_winning_counts(line):
            return

    # -------------------------------
    #   Handle Methods
    # -------------------------------

    def handle_round_header(self, line: str) -> bool:
        match = self.round_header_pattern.match(line)
        if match:
            # finalize old round
            self.finalize_current_round()

            round_number = int(match.group(1))
            p1 = match.group(2)
            p1_score = int(match.group(3))
            p2 = match.group(4)
            p2_score = int(match.group(5))

            # create new RoundData
            self.current_round = RoundData(
                round_number=round_number,
                score_at_start={"A": 0, "B": 0},
                bounties={"A": self.bounty["A"], "B": self.bounty["B"]},
                players={"A": {"hole_cards": None}, "B": {"hole_cards": None}},
                blinds={},
                streets=[],
                awards={"A": 0, "B": 0},
                winning_counts_end_round={"A": None, "B": None},
                showdown=Showdown(),
            )
            # set actual scores
            self.current_round.score_at_start[p1] = p1_score
            self.current_round.score_at_start[p2] = p2_score

            # reset pot/chips
            self.pot = 0
            self.player_stacks = {"A": 400, "B": 400}
            self.player_contributions = {"A": 0, "B": 0}

            # start with preflop street
            self.current_round.streets.append(
                Street(street_name="preflop", community_cards=[], actions=[])
            )

            return True
        return False

    def handle_bounty_reset(self, line: str) -> bool:
        match = self.bounty_reset_pattern.match(line)
        if match and self.current_round:
            valA = match.group(1)
            plA = match.group(2)
            valB = match.group(3)
            plB = match.group(4)
            self.bounty[plA] = valA
            self.bounty[plB] = valB
            self.current_round.bounties[plA] = valA
            self.current_round.bounties[plB] = valB
            return True
        return False

    def handle_blind(self, line: str) -> bool:
        match = self.blind_pattern.match(line)
        if match and self.current_round:
            player = match.group(1)
            amt = int(match.group(2))

            # If small_blind not set, set it; else big_blind
            if "small_blind" not in self.current_round.blinds:
                self.current_round.blinds["small_blind"] = {
                    "player": player,
                    "amount": amt,
                }
            else:
                self.current_round.blinds["big_blind"] = {
                    "player": player,
                    "amount": amt,
                }

            # record action
            self.current_round.streets[-1].actions.append(
                {"player": player, "action": "post_blind", "amount": amt}
            )

            return True
        return False

    def handle_dealt_cards(self, line: str) -> bool:
        match = self.dealt_pattern.match(line)
        if match and self.current_round:
            player = match.group(1)
            c1 = match.group(2)
            c2 = match.group(3)
            self.current_round.players[player]["hole_cards"] = [c1, c2]
            return True
        return False

    def handle_action(self, line: str) -> bool:
        match = self.action_pattern.match(line)
        if match and self.current_round:
            player = match.group(1)
            raw_action = match.group(2).lower()

            action_type = ""
            amount_num = 0

            if raw_action.startswith("raises to"):
                amt_str = raw_action.split("raises to")[-1].strip()
                amount_num = int(amt_str)
                action_type = "raise"
                self.current_round.streets[-1].player_contributions_during_street[
                    player
                ] = amount_num

            elif raw_action.startswith("bets"):
                amt_str = raw_action.split("bets")[-1].strip()
                amount_num = int(amt_str)
                action_type = "bet"
                self.current_round.streets[-1].player_contributions_during_street[
                    player
                ] = amount_num

            elif raw_action == "calls":
                action_type = "call"
                other = "A" if player == "B" else "B"
                other_contribution_during_street = self.current_round.streets[
                    -1
                ].player_contributions_during_street[other]
                amount_num = other_contribution_during_street
                self.current_round.streets[-1].player_contributions_during_street[
                    player
                ] = amount_num

            elif raw_action == "checks":
                action_type = "check"

            elif raw_action == "folds":
                action_type = "fold"

            self.current_round.streets[-1].actions.append(
                {"player": player, "action": action_type, "amount": amount_num}
            )
            return True
        return False

    def handle_flop_turn_river(self, line: str) -> bool:
        match = self.flop_turn_river_pattern.match(line)
        if match and self.current_round:
            self.finalize_current_street()
            street_keyword = match.group(1).lower()
            card_string = match.group(2)
            community_cards = card_string.split()

            new_street = Street(
                street_name=street_keyword, community_cards=community_cards, actions=[]
            )
            self.current_round.streets.append(new_street)
            return True
        return False

    def handle_stacks_line(self, line: str) -> bool:
        # "Current stacks: 394, 394"
        # We can ignore or cross-check.
        match = self.stacks_pattern.match(line)
        if match:
            # Cross-check or store if needed
            return True
        return False

    def handle_shows_line(self, line: str) -> bool:
        match = self.shows_pattern.match(line)
        if match and self.current_round:
            player = match.group(1)
            c1 = match.group(2)
            c2 = match.group(3)
            # store in showdown
            self.current_round.showdown.final_hole_cards[player] = [c1, c2]
            return True
        return False

    def handle_awarded(self, line: str) -> bool:
        match = self.awarded_pattern.match(line)
        if match and self.current_round:
            player = match.group(1)
            amt = int(match.group(2))
            self.current_round.awards[player] += amt
            return True
        return False

    def handle_winning_counts(self, line: str) -> bool:
        match = self.winning_pattern.match(line)
        if match and self.current_round:
            self.finalize_current_street()
            # parse the final scoreboard
            pA = match.group(1)
            pA_val = int(match.group(2))
            pB = match.group(3)
            pB_val = int(match.group(4))
            self.current_round.winning_counts_end_round[pA] = pA_val
            self.current_round.winning_counts_end_round[pB] = pB_val

            # detect fold vs showdown
            folded_player = None
            actions_all = []
            for s in self.current_round.streets:
                actions_all.extend(s.actions)

            for a in actions_all:
                if a["action"] == "fold":
                    folded_player = a["player"]
                    break

            if folded_player:
                # no showdown
                self.current_round.showdown.went_to_showdown = False
                winner = "A" if folded_player == "B" else "B"
                self.current_round.showdown.winner = winner
                self.current_round.showdown.winning_amount = self.current_round.awards[
                    winner
                ]
            else:
                # showdown
                self.current_round.showdown.went_to_showdown = True
                a_award = self.current_round.awards["A"]
                b_award = self.current_round.awards["B"]
                if a_award > b_award:
                    self.current_round.showdown.winner = "A"
                    self.current_round.showdown.winning_amount = a_award
                elif b_award > a_award:
                    self.current_round.showdown.winner = "B"
                    self.current_round.showdown.winning_amount = b_award
                else:
                    self.current_round.showdown.winner = None
                    self.current_round.showdown.winning_amount = 0

            # Fill in any missing hole cards from "players"
            for pl in ["A", "B"]:
                if pl not in self.current_round.showdown.final_hole_cards:
                    self.current_round.showdown.final_hole_cards[pl] = None

            # Bounty check
            winner_id = self.current_round.showdown.winner
            if winner_id in ("A", "B"):
                for card in self.current_round.players[winner_id]["hole_cards"]:
                    if card[0] == self.bounty[winner_id]:
                        self.current_round.bounty_awarded = True
                        break

                for card in self.current_round.streets[-1].community_cards:
                    if card[0] == self.bounty[winner_id]:
                        self.current_round.bounty_awarded = True
                        break

            return True
        return False

    # -------------------------------
    #   Utility / Finalization
    # -------------------------------

    def finalize_current_street(self):
        """Populates pot/stacks/contributions info into the last Street."""
        if self.current_round and self.current_round.streets:
            last_street = self.current_round.streets[-1]
            for player in ["A", "B"]:
                self.pot += last_street.player_contributions_during_street[player]
                self.player_stacks[player] -= last_street.player_contributions_during_street[player]
                self.player_contributions[player] += last_street.player_contributions_during_street[player]

            last_street.pot_size_after_street = self.pot
            last_street.player_stacks_after_street = dict(self.player_stacks)
            last_street.player_contributions_after_street = dict(
                self.player_contributions
            )

    def finalize_current_round(self):
        """If there's a round in progress, finalize the last street and push it into rounds."""
        if self.current_round:
            self.rounds.append(self.current_round)
            self.current_round = None
