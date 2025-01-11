// app/rounds/[roundNumber]/page.tsx

import { notFound } from "next/navigation";
import { getAllRounds } from "@/app/lib/pokerData";
import { RoundData } from "@/types/poker";

export async function generateStaticParams() {
  const rounds = getAllRounds();
  // Return an array of objects: { roundNumber: "1" }, etc.
  return rounds.map((rd) => ({
    roundNumber: rd.round_number.toString(),
  }));
}

// If you want SSG (Static Site Generation), declare revalidate or not
export const revalidate = 3600; // optional: re-gen this page every hour, for example

interface RoundPageProps {
  params: {
    roundNumber: string;
  };
}

// This is the server component for each round
export default function RoundPage({ params }: RoundPageProps) {
  const roundNum = parseInt(params.roundNumber, 10);
  const rounds = getAllRounds();
  const roundData = rounds.find((r) => r.round_number === roundNum);

  if (!roundData) {
    // If no matching round, you can throw a 404
    notFound();
  }

  return (
    <main style={{ padding: "1rem" }}>
      <RoundDetails round={roundData!} />
    </main>
  );
}

// Let's separate out a child component for the details
function RoundDetails({ round }: { round: RoundData }) {
  const {
    round_number,
    score_at_start,
    bounties,
    players,
    blinds,
    streets,
    awards,
    showdown,
    bounty_awarded
  } = round;

  return (
    <div>
      <h1>Round #{round_number}</h1>
      <p>
        <strong>Score at start:</strong> A={score_at_start.A}, B={score_at_start.B}
      </p>
      <p>
        <strong>Bounties:</strong> A={bounties.A}, B={bounties.B}{" "}
        {bounty_awarded && <em>(Bounty Awarded!)</em>}
      </p>
      <p>
        <strong>Hole Cards (A):</strong> {players.A.hole_cards.join(" ")} <br />
        <strong>Hole Cards (B):</strong> {players.B.hole_cards.join(" ")}
      </p>
      <p>
        <strong>Blinds:</strong><br />
        Small Blind: {blinds.small_blind.player} ({blinds.small_blind.amount}) <br />
        Big Blind: {blinds.big_blind.player} ({blinds.big_blind.amount})
      </p>

      <hr />
      <h2>Streets</h2>
      {streets.map((st, idx) => (
        <div
          key={idx}
          style={{
            border: "1px solid #ccc",
            marginBottom: "1rem",
            padding: "0.5rem",
          }}
        >
          <h3>{st.street_name.toUpperCase()}</h3>
          <p>
            <strong>Community Cards:</strong> {st.community_cards.join(" ")}
          </p>
          <p>
            <strong>Actions:</strong>
          </p>
          <ul>
            {st.actions.map((action, i) => (
              <li key={i}>
                {action.player} {action.action}
                {action.amount !== undefined && ` ${action.amount}`}
              </li>
            ))}
          </ul>
          <p>
            <strong>Pot Size After Street:</strong> {st.pot_size_after_street}
          </p>
          <p>
            <strong>Stacks:</strong>{" "}
            A={st.player_stacks_after_street.A}, B={st.player_stacks_after_street.B}
          </p>
        </div>
      ))}

      <hr />
      <h2>Final Awards</h2>
      <p>
        A: {awards.A}, B: {awards.B}
      </p>

      <h2>Showdown</h2>
      {showdown.went_to_showdown ? (
        <>
          <p>
            <strong>Winner:</strong> {showdown.winner ?? "Tie/None"} <br />
            <strong>Winning Amount:</strong> {showdown.winning_amount}
          </p>
          <p>
            <strong>Final Hole Cards:</strong>
            <br />
            A: {showdown.final_hole_cards.A?.join(" ")} <br />
            B: {showdown.final_hole_cards.B?.join(" ")}
          </p>
        </>
      ) : (
        <p>No Showdown (fold occurred)</p>
      )}
    </div>
  );
}