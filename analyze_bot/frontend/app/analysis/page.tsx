'use client';

import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

const AnalysisPage = () => {
  const [data, setData] = useState([]);
  const [streetFilter, setStreetFilter] = useState("ALL"); // Default filter

  // Define filter options
  const streetOptions = ["ALL", "preflop", "flop", "turn", "river", "showdown"];

  // Fetch data based on the filter
  useEffect(() => {
    const fetchData = async () => {
      if (streetFilter === "ALL") {
        // Make 6 separate API calls for each street
        const allStreets = ["preflop", "flop", "turn", "river", "showdown", "ALL"];
        const responses = await Promise.all(
          allStreets.map((street) =>
            fetch(`http://10.29.251.249:5050/analysis/rounds?street=${street}`).then((res) =>
              res.json()
            )
          )
        );

        // Combine responses into a single dataset for plotting
        const combinedData = responses.map((streetData, index) => ({
          x: streetData.map((d) => d.roundNumber),
          y: streetData.map((d) => d.awardA),
          type: "scatter",
          mode: "lines+markers",
          name: allStreets[index], // Label each dataset by street
        }));

        setData(combinedData);
      } else {
        // Single API call for a specific street
        const response = await fetch(
          `http://10.29.251.249:5050/analysis/rounds?street=${streetFilter}`
        );
        const singleData = await response.json();

        setData([
          {
            x: singleData.map((d) => d.roundNumber),
            y: singleData.map((d) => d.awardA),
            type: "scatter",
            mode: "lines+markers",
            marker: { color: "#4e54c8" },
            name: streetFilter, // Label the dataset
          },
        ]);
      }
    };

    fetchData();
  }, [streetFilter]); // Refetch when streetFilter changes

  return (
    <div
      style={{
        padding: "2rem",
        background: "linear-gradient(135deg, #e4e5f1, #e8e8e8)",
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: "12px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
          padding: "2rem",
          width: "100%",
          maxWidth: "800px",
        }}
      >
        <h1 style={{ textAlign: "center", color: "#333" }}>Round Analysis</h1>

        {/* Dropdown for Street Filter */}
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="street-filter" style={{ marginRight: "0.5rem" }}>
            Filter by Street:
          </label>
          <select
            id="street-filter"
            value={streetFilter}
            onChange={(e) => setStreetFilter(e.target.value)}
            style={{
              padding: "0.5rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
          >
            {streetOptions.map((option) => (
              <option key={option} value={option}>
                {option.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Plot */}
        <Plot
          data={data}
          layout={{
            title: "Round # vs. A's Winnings",
            xaxis: { title: "Round #" },
            yaxis: { title: "A's Winnings" },
            showlegend: true, // Show legend for all datasets
          }}
        />
      </div>
    </div>
  );
};

export default AnalysisPage;