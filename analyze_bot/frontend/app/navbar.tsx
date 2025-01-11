// Redesigned Navbar
export default function Navbar() {
    return (
      <nav style={{ padding: "1rem", background: "#4e54c8", borderRadius: "12px" }}>
        <a href="/" className="nav-link">
          Home
        </a>
        <a href="/analysis" className="nav-link">
          Analysis
        </a>
      </nav>
    );
  }