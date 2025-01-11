// app/page.tsx
import Link from "next/link";
import { getAllRounds } from "./lib/pokerData";
import { RoundData } from "@/types/poker";

// Styling for the main container
const mainStyle = {
  padding: '2rem',
  backgroundColor: '#f9fafb', // Light background
  minHeight: '100vh',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
};

const cardStyle = {
  background: '#ffffff', // White card
  borderRadius: '12px',
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  padding: '2rem',
  maxWidth: '600px',
  width: '100%',
  textAlign: 'center',
};

// Update your HomePage Component
export default function HomePage() {
  const rounds = getAllRounds();

  return (
    <main style={mainStyle}>
      <div style={cardStyle}>
        <h1 style={{ marginBottom: '1.5rem', fontSize: '2rem', color: '#333' }}>
          All Pokerbot Rounds
        </h1>
        <ul>
          {rounds.map((rd) => (
            <li
              key={rd.round_number}
              style={{
                margin: '0.5rem 0',
                listStyle: 'none',
              }}
            >
              <a
                href={`/rounds/${rd.round_number}`}
                style={{
                  color: '#4e54c8',
                  textDecoration: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  transition: 'background 0.3s',
                }}
              >
                Round #{rd.round_number} | Awards: A={rd.awards.A}, B={rd.awards.B}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}