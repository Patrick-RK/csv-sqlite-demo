/**
 * Upload logic — drop zone, file picker, CSV parsing, and uploading to the server.
 *
 * Handles:
 *  - Drag-and-drop or click to pick a local CSV file
 *  - Choosing a CSV from the server's data folder
 *  - Previewing the CSV in a table
 *  - Rendering charts from the CSV data
 *  - Uploading the CSV to the database
 */

let selectedFile = null;

const drop = document.getElementById('drop');
const fi = document.getElementById('file');
const thead = document.getElementById('thead');
const tbody = document.getElementById('tbody');
const btn = document.getElementById('upload');
const fname = document.getElementById('fname');
const status = document.getElementById('status');
const chartsDiv = document.getElementById('charts');
const toggle = document.getElementById('toggle');
const tableWrap = document.getElementById('tableWrap');
const filePicker = document.getElementById('filePicker');
const fileSelect = document.getElementById('fileSelect');
const pickBtn = document.getElementById('pickBtn');
const orDivider = document.getElementById('orDivider');

// --- CSV parsing ---

function parseCSV(text) {
  const lines = text.trim().split('\n').map(l => l.split(','));
  return {
    headers: lines[0].map(h => h.trim()),
    rows: lines.slice(1).map(r => r.map(c => c.trim())),
  };
}

// --- Table preview ---

function toggleTable() {
  toggle.classList.toggle('collapsed');
  tableWrap.classList.toggle('collapsed');
}

function showTable(headers, rows) {
  thead.innerHTML = '<tr>' + headers.map(h => '<th>' + h + '</th>').join('') + '</tr>';
  tbody.innerHTML = rows.map(r => '<tr>' + r.map(c => '<td>' + c + '</td>').join('') + '</tr>').join('');
  toggle.style.display = 'block';
  toggle.classList.remove('collapsed');
  tableWrap.classList.remove('collapsed');
}

// --- Charts ---

function showCharts(headers, rows) {
  const di = headers.indexOf('date');
  const ti = headers.indexOf('temp_c');
  const hi = headers.indexOf('humidity');
  if (di < 0 || ti < 0 || hi < 0) { chartsDiv.style.display = 'none'; return; }
  const dates = [], temps = [], humidities = [];
  rows.forEach(r => {
    dates.push(r[di]);
    temps.push(parseFloat(r[ti]));
    humidities.push(parseFloat(r[hi]));
  });
  chartsDiv.style.display = 'block';
  renderTemperatureChart(dates, temps);
  renderHumidityChart(dates, humidities);
}

// --- Drop zone ---

drop.addEventListener('click', () => fi.click());
drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('over'); });
drop.addEventListener('dragleave', () => drop.classList.remove('over'));
drop.addEventListener('drop', e => { e.preventDefault(); drop.classList.remove('over'); handleFile(e.dataTransfer.files[0]); });
fi.addEventListener('change', () => handleFile(fi.files[0]));

function handleFile(f) {
  if (!f) return;
  selectedFile = f;
  fname.textContent = f.name;
  const r = new FileReader();
  r.onload = e => {
    const { headers, rows } = parseCSV(e.target.result);
    showTable(headers, rows);
    showCharts(headers, rows);
    btn.style.display = 'inline-block';
    status.textContent = '';
  };
  r.readAsText(f);
}

// --- Upload to database ---

btn.addEventListener('click', async () => {
  const name = selectedFile.name.replace(/\.csv$/i, '');
  const fd = new FormData();
  fd.append('file', selectedFile);
  fd.append('dataset', name);
  status.textContent = 'uploading...';
  const res = await fetch('/upload', { method: 'POST', body: fd });
  const j = await res.json();
  status.textContent = 'inserted ' + j.inserted + ' row(s) into database';
  loadDatasets();
});

// --- File picker (load CSVs from the server's data folder) ---

async function loadFiles() {
  const res = await fetch('/files');
  const files = await res.json();
  if (!files.length) return;
  filePicker.style.display = 'block';
  orDivider.style.display = 'block';
  fileSelect.innerHTML = '<option value="">-- select a file --</option>' +
    files.map(f => '<option value="' + f + '">' + f + '</option>').join('');
}

pickBtn.addEventListener('click', async () => {
  const name = fileSelect.value;
  if (!name) return;
  const res = await fetch('/files/' + encodeURIComponent(name));
  const text = await res.text();
  const { headers, rows } = parseCSV(text);
  showTable(headers, rows);
  showCharts(headers, rows);
  selectedFile = new File([text], name, { type: 'text/csv' });
  fname.textContent = name;
  btn.style.display = 'inline-block';
  status.textContent = '';
});

loadFiles();
