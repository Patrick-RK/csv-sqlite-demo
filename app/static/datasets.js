/**
 * Datasets — loads saved datasets from the database and renders tabs.
 *
 * Handles:
 *  - Fetching the list of dataset names from /datasets
 *  - Rendering a tab for each one
 *  - Loading a dataset's rows when you click a tab
 *  - Showing the data in the table and charts
 */

const tabsDiv = document.getElementById('tabs');

async function loadDatasets() {
  const res = await fetch('/datasets');
  const datasets = await res.json();
  if (!datasets.length) { tabsDiv.style.display = 'none'; return; }
  tabsDiv.style.display = 'flex';
  tabsDiv.innerHTML = datasets.map(d =>
    '<button class="tab" data-name="' + d + '">' + d + '</button>'
  ).join('');
  tabsDiv.querySelectorAll('.tab').forEach(t =>
    t.addEventListener('click', () => selectDataset(t.dataset.name))
  );
}

async function selectDataset(name) {
  tabsDiv.querySelectorAll('.tab').forEach(t =>
    t.classList.toggle('active', t.dataset.name === name)
  );
  const res = await fetch('/datasets/' + encodeURIComponent(name));
  const data = await res.json();
  if (!data.length) return;
  const headers = Object.keys(data[0]);
  const rows = data.map(r => headers.map(h => String(r[h])));
  showTable(headers, rows);
  showCharts(headers, rows);
  chartsDiv.style.display = 'block';
  status.textContent = 'showing ' + data.length + ' rows from database';
}

loadDatasets();
