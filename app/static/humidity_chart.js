/**
 * Humidity bar chart.
 *
 * Call renderHumidityChart(dates, humidities) with arrays of
 * date strings and humidity numbers to draw the chart
 * into the #chart-humidity element.
 */
function renderHumidityChart(dates, humidities) {
  const layout = {
    paper_bgcolor: '#0f1117',
    plot_bgcolor: '#0f1117',
    font: { family: 'JetBrains Mono', color: '#94a3b8', size: 11 },
    xaxis: { gridcolor: '#1e293b', linecolor: '#334155' },
    yaxis: { gridcolor: '#1e293b', linecolor: '#334155', range: [0, 100] },
    margin: { l: 50, r: 30, t: 40, b: 40 },
    hovermode: 'x unified',
    title: { text: 'Humidity (%)', font: { size: 13, color: '#e2e8f0' } },
  };

  const trace = {
    x: dates,
    y: humidities,
    type: 'bar',
    name: 'humidity',
    marker: { color: '#818cf8', opacity: 0.8 },
    hovertemplate: '%{y}%<extra></extra>',
  };

  Plotly.newPlot('chart-humidity', [trace], layout, { responsive: true });
}
