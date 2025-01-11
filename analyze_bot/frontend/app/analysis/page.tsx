'use client'

import React, { useEffect, useState } from 'react';
const Plot = require('react-plotly.js').default;

const analysisStyle = {
  padding: '2rem',
  background: 'linear-gradient(135deg, #e4e5f1, #e8e8e8)',
  minHeight: '100vh',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
};

const plotCardStyle = {
  background: '#fff',
  borderRadius: '12px',
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  padding: '2rem',
  width: '100%',
  maxWidth: '800px',
};


const AnalysisPage = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('http://10.29.251.249:5050/analysis/rounds')
      .then(response => response.json())
      .then(data => setData(data));
  }, []);

  const plotData = [
    {
      x: data.map(d => d.roundNumber),
      y: data.map(d => d.awardA),
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: 'red' },
    },
  ];

  return (
    <div style={analysisStyle}>
      <div style={plotCardStyle}>
        <h1 style={{ textAlign: 'center', color: '#333' }}>Round Analysis</h1>
        <Plot
          data={[
            {
              x: data.map((d) => d.roundNumber),
              y: data.map((d) => d.awardA),
              type: 'scatter',
              mode: 'lines+markers',
              marker: { color: '#4e54c8' },
            },
          ]}
          layout={{
            title: "Round # vs. A's Winnings",
            xaxis: { title: 'Round #' },
            yaxis: { title: "A's Winnings" },
          }}
        />
      </div>
    </div>
  );
};

export default AnalysisPage;
