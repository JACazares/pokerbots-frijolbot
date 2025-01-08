// Fetch and display the rounds from gamelog.json
document.addEventListener("DOMContentLoaded", () => {
    fetch("gamelog.json")
      .then((res) => res.json())
      .then((data) => {
        populateRoundList(data);
      })
      .catch((err) => {
        console.error("Error loading gamelog JSON:", err);
      });
  });
  
  function populateRoundList(rounds) {
    const roundList = document.getElementById("roundList");
    roundList.innerHTML = ""; // Clear existing
  
    rounds.forEach((round) => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.textContent = `Round #${round.round_number}`;
      li.addEventListener("click", () => showRoundDetails(round));
      roundList.appendChild(li);
    });
  }
  
  function showRoundDetails(round) {
    const detailsDiv = document.getElementById("roundDetails");
  
    // Build an HTML snippet with relevant info
    const {
      round_number,
      score_at_start,
      bounties,
      blinds,
      players,
      streets,
      awards,
      winning_counts_end_round
    } = round;
  
    // Basic info
    let html = `
      <h5>Round #${round_number}</h5>
      <p><strong>Score at start:</strong> A=${score_at_start.A}, B=${score_at_start.B}</p>
      <p><strong>Bounties:</strong> A=${bounties.A}, B=${bounties.B}</p>
      <p><strong>Blinds:</strong> 
         Small Blind: ${blinds.small_blind?.player} (${blinds.small_blind?.amount}),
         Big Blind: ${blinds.big_blind?.player} (${blinds.big_blind?.amount})
      </p>
      <p><strong>Hole Cards:</strong><br>
         A: ${players.A.hole_cards ? players.A.hole_cards.join(" ") : "?? ??"} <br>
         B: ${players.B.hole_cards ? players.B.hole_cards.join(" ") : "?? ??"}
      </p>
  
      <h6>Streets</h6>
    `;
  
    // Streets
    streets.forEach((street) => {
      const { street_name, community_cards, actions } = street;
      // If no community cards, it’s preflop or no flop
      const cardsString = community_cards && community_cards.length
        ? community_cards.join(" ")
        : "(none)";
  
      html += `
        <div class="mb-2">
          <strong>${street_name.toUpperCase()}:</strong> ${cardsString}
          <ul>
      `;
      actions.forEach((action) => {
        html += `<li>${action.player} ${action.action} ${action.amount ?? ""}</li>`;
      });
      html += `</ul></div>`;
    });
  
    html += `
      <p><strong>Awards:</strong> A=${awards.A}, B=${awards.B}</p>
      <p><strong>Winning counts at end of round:</strong> 
         A=${winning_counts_end_round.A}, 
         B=${winning_counts_end_round.B}
      </p>
    `;
  
    detailsDiv.innerHTML = html;
  }