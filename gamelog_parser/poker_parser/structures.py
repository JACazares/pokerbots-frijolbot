from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Showdown:
    went_to_showdown: bool = False
    winner: Optional[str] = None       # "A", "B", or None if a tie
    winning_amount: int = 0
    final_hole_cards: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class Street:
    street_name: str
    community_cards: List[str] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)  # e.g. [{"player":"A","action":"raise","amount":10}]
    pot_size_after_street: int = 0
    player_stacks_after_street: Dict[str, int] = field(
        default_factory=lambda: {"A": 400, "B": 400}
    )
    player_contributions_after_street: Dict[str, int] = field(
        default_factory=lambda: {"A": 0, "B": 0}
    )

@dataclass
class RoundData:
    round_number: int
    score_at_start: Dict[str, int]             # e.g. {"A": -10, "B": 20}
    bounties: Dict[str, Optional[int]]         # e.g. {"A": 7, "B": 3}
    players: Dict[str, Dict]                   # e.g. {"A": {"hole_cards": [..]}, "B": {...}}
    blinds: Dict[str, Dict]                    # e.g. {"small_blind": {...}, "big_blind": {...}}
    streets: List[Street]
    awards: Dict[str, int]                     # net change per player
    winning_counts_end_round: Dict[str, int]
    showdown: Showdown
    bounty_awarded: bool = False