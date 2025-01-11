// types/poker.ts

export interface Showdown {
    went_to_showdown: boolean;
    winner?: string | null;        // "A", "B", or null if tie
    winning_amount: number;
    final_hole_cards: Record<string, string[]>;
  }
  
  export interface StreetAction {
    player: string;    // "A" or "B"
    action: string;    // "raise", "call", "fold", etc.
    amount?: number;   // optional
  }
  
  export interface Street {
    street_name: string;                    // "preflop", "flop", "turn", "river"
    community_cards: string[];
    actions: StreetAction[];
    player_contributions_during_street: Record<string, number>;
    pot_size_after_street: number;
    player_stacks_after_street: Record<string, number>;
    player_contributions_after_street: Record<string, number>;
  }
  
  export interface RoundData {
    round_number: number;
    score_at_start: Record<string, string>; // e.g. { "A": "-10", "B": "20" }
    bounties: Record<string, number | null>;
    players: Record<string, { hole_cards: string[] }>;
    blinds: Record<string, { player: string; amount: number }>;
    streets: Street[];
    awards: Record<string, number>;
    winning_counts_end_round: Record<string, number>;
    showdown: Showdown;
    bounty_awarded: boolean;
  }