/**
 * Temperature line chart.
 *
 * Call renderTemperatureChart(dates, temps) with arrays of
 * date strings and temperature numbers to draw the chart
 * into the #chart-temp element.
 */
function renderTemperatureChart(dates, temps) {
  const layout = {
    paper_bgcolor: '#0f1117',
    plot_bgcolor: '#0f1117',
    font: { family: 'JetBrains Mono', color: '#94a3b8', size: 11 },
    xaxis: { gridcolor: '#1e293b', linecolor: '#334155' },
    yaxis: { gridcolor: '#1e293b', linecolor: '#334155' },
    margin: { l: 50, r: 30, t: 40, b: 40 },
    hovermode: 'x unified',
    title: { text: 'Temperature (°C)', font: { size: 13, color: '#e2e8f0' } },
  };

  const trace = {
    x: dates,
    y: temps,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'temp',
    line: { color: '#38bdf8', width: 2 },
    marker: { size: 5, color: '#38bdf8' },
    hovertemplate: '%{y}°C<extra></extra>',
  };

  Plotly.newPlot('chart-temp', [trace], layout, { responsive: true });
}
