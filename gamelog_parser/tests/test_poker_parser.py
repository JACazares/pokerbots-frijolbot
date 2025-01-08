import pytest
from poker_parser.parser_logic import PokerLogParser

def test_preflop_fold():
    """
    Tests that a fold occurring preflop is handled correctly.
    Checks awarding logic, pot, net awards, no showdown, etc.
    """
    log_text = """\
6.9630 MIT Pokerbots - A vs B

Round #1, A (0), B (0)
Bounties reset to 5 for player A and K for player B
A posts the blind of 1
B posts the blind of 2
A dealt [Qc Th]
B dealt [3d 2s]
A folds
A awarded -1
B awarded 1
Winning counts at the end of the round: , A (-1), B (1)
"""

    parser = PokerLogParser()
    results = parser.parse_string(log_text)

    assert len(results) == 1, "Should have exactly 1 round parsed"
    round_data = results[0]

    # Basic checks
    assert round_data["round_number"] == 1
    assert round_data["bounties"]["A"] == "5"
    assert round_data["bounties"]["B"] == "K"

    # Check that the fold ended action and awarding is correct
    # A folds, so B should win
    assert round_data["awards"]["A"] == -1
    assert round_data["awards"]["B"] == 1

    # Showdown check
    showdown = round_data["showdown"]
    assert showdown["went_to_showdown"] is False
    assert showdown["winner"] == "B"
    assert showdown["winning_amount"] == 1


def test_postflop_fold():
    """
    Tests that a fold on the flop is handled correctly.
    """
    log_text = """\
Round #1, B (10), A (20)
Bounties reset to 2 for player B and 3 for player A
B posts the blind of 1
A posts the blind of 2
B dealt [6d 9d]
A dealt [4h 4c]
B calls
A checks
Flop [Ks 7s 2h], B (2), A (2)
Current stacks: 398, 398
A checks
B bets 2
A folds
B awarded 10
A awarded -10
Winning counts at the end of the round: , B (20), A (10)
"""

    parser = PokerLogParser()
    results = parser.parse_string(log_text)

    assert len(results) == 1
    rd = results[0]

    assert rd["round_number"] == 1
    # B started with 10, A with 20 (just an example scoreboard).
    assert rd["score_at_start"]["B"] == 10
    assert rd["score_at_start"]["A"] == 20
    assert rd["bounties"]["B"] == "2"
    assert rd["bounties"]["A"] == "3"

    # B calls, A checks, flop deals -> A checks, B bets, A folds
    # B should get net awarding of +10, A -10
    assert rd["awards"]["B"] == 10
    assert rd["awards"]["A"] == -10

    # No showdown
    assert not rd["showdown"]["went_to_showdown"]
    assert rd["showdown"]["winner"] == "B"


def test_showdown_no_fold():
    """
    Tests a full round with calls all the way to showdown.
    Ensures pot tracking, awarding, and final hole cards are captured.
    """
    log_text = """\
Round #2, A (-6), B (6)
A posts the blind of 1
B posts the blind of 2
A dealt [8c 8d]
B dealt [Qc 7d]
A raises to 4
B calls
Flop [8h Ts Js], A (4), B (4)
B checks
A checks
Turn [8h Ts Js Ac], A (4), B (4)
B checks
A checks
River [8h Ts Js Ac Jc], A (4), B (4)
B bets 2
A calls
A shows [8c 8d]
B shows [Qc 7d]
A awarded 6
B awarded -6
Winning counts at the end of the round: , A (0), B (0)
"""

    parser = PokerLogParser()
    results = parser.parse_string(log_text)
    assert len(results) == 1
    rd = results[0]

    # Round #2, scoreboard A(-6), B(6)
    assert rd["round_number"] == 2
    assert rd["score_at_start"]["A"] == -6
    assert rd["score_at_start"]["B"] == 6

    # No folds, so showdown
    showdown = rd["showdown"]
    assert showdown["went_to_showdown"] is True
    # A is winner
    assert showdown["winner"] == "A"
    assert showdown["winning_amount"] == 6
    # Hole cards at showdown
    assert showdown["final_hole_cards"]["A"] == ["8c", "8d"]
    assert showdown["final_hole_cards"]["B"] == ["Qc", "7d"]

    # Awards
    assert rd["awards"]["A"] == 6
    assert rd["awards"]["B"] == -6


def test_round_header_order_swap():
    """
    Ensures we handle logs that say 
    'Round #1, B (10), A (0)' 
    and we still map the scoreboard properly.
    """
    log_text = """\
Round #1, B (10), A (0)
Bounties reset to 5 for player B and 5 for player A
B posts the blind of 1
A posts the blind of 2
B dealt [Qh Js]
A dealt [2d 7s]
B folds
B awarded -1
A awarded 1
Winning counts at the end of the round: , B (9), A (1)
"""

    parser = PokerLogParser()
    results = parser.parse_string(log_text)
    assert len(results) == 1
    rd = results[0]
    # The log says "B (10), A (0)" 
    assert rd["score_at_start"]["B"] == 10
    assert rd["score_at_start"]["A"] == 0
    assert rd["bounties"]["B"] == "5"
    assert rd["bounties"]["A"] == "5"

    # B folds immediately, awarding
    assert rd["awards"]["B"] == -1
    assert rd["awards"]["A"] == 1
    # fold => no showdown
    assert not rd["showdown"]["went_to_showdown"]
    assert rd["showdown"]["winner"] == "A"


def test_bounty_trigger():
    """
    Tests a scenario where the winner's net award 
    clearly exceeds the other player's contribution 
    (implying the bounty was triggered).
    """
    log_text = """\
Round #1, A (0), B (0)
Bounties reset to 5 for player A and 7 for player B
A posts the blind of 1
B posts the blind of 2
A dealt [Qc Th]
B dealt [3d 2s]
A calls
B checks
Flop [3s Ts Qs], A (2), B (2)
B bets 2
A calls
Turn [3s Ts Qs 7c], A (4), B (4)
B bets 2
A calls
River [3s Ts Qs 7c 5c], A (6), B (6)
B bets 2
A calls
A shows [Qc Th]
B shows [3d 2s]
A awarded 22
B awarded -22
Winning counts at the end of the round: , A (22), B (-22)
"""
    parser = PokerLogParser()
    results = parser.parse_string(log_text)
    assert len(results) == 1
    rd = results[0]

    # Check awarding
    assert rd["awards"]["A"] == 22
    assert rd["awards"]["B"] == -22
    # A's total call contributions are presumably < 22 if we sum the bets
    # So this suggests a bounty was triggered
    assert rd["bounty_awarded"] is True