# CSV → SQLite Demo

## Quick start

```bash
git clone https://github.com/Patrick-RK/csv-sqlite-demo.git
cd csv-sqlite-demo
docker compose up --build -d
python scripts/seed_database.py
open http://localhost:8001
```

To stop: `docker compose down` (keeps data) or `docker compose down -v` (wipes data).

---

## The pieces

```
csv-sqlite-demo/
├── docker-compose.yml   # Runs the app in a container with a persistent volume
├── Dockerfile           # Builds the Python image (installs dependencies, copies code)
├── requirements.txt     # Python packages: fastapi, sqlalchemy, uvicorn, python-multipart
├── app/                 # The server, website, and chart code
├── data/                # CSV files you can upload
└── scripts/             # Seed and test scripts
```

---

## The app folder

```
app/
├── database.py          # Database connection, table definition, helper functions
├── server.py            # The routes — what the server can do
├── static/
│   ├── css/
│   │   └── styles.css           # All the styling
│   └── js/
│       ├── temperature_chart.js # Temperature line chart
│       ├── humidity_chart.js    # Humidity bar chart
│       ├── upload.js            # Drop zone, file picker, CSV parsing, upload
│       └── datasets.js          # Tabs — loading saved datasets from the database
└── templates/
    └── website.html     # Just the HTML structure (no styles, no logic)
```

---

## The database (`app/database.py`)

This file sets up three things:

**1. The connection** — points SQLAlchemy at a SQLite file (`weather.db`).

**2. The table** — defines what a row looks like:

```
┌──────────────────────────────────────────────────┐
│  weather table                                   │
├──────┬──────────┬────────────┬────────┬──────────┤
│  id  │ dataset  │    date    │ temp_c │ humidity │
├──────┼──────────┼────────────┼────────┼──────────┤
│  1   │ winter   │ 2026-01-01 │  3.0   │  78.0    │
│  2   │ winter   │ 2026-01-02 │  1.0   │  82.0    │
│ ...  │  ...     │    ...     │  ...   │  ...     │
└──────┴──────────┴────────────┴────────┴──────────┘
```

The `dataset` column groups rows together so you can upload multiple CSVs (e.g. "winter", "spring", "summer") and switch between them.

**3. Two helpers:**
- `get_db()` — opens a database session and automatically closes it when done. Every route in the server uses this instead of manually opening/closing connections.
- `Weather.to_dict()` — converts a row into a Python dictionary so the server can return it as JSON.

---

## The server (`app/server.py`)

A Python app built with **FastAPI**. It imports the model and helpers from `database.py`, and exposes these routes:

| Route | What it does |
|-------|-------------|
| `GET /` | Serve the website |
| `GET /files` | List available CSV files in the data folder |
| `GET /files/{name}` | Return the contents of a CSV file |
| `POST /upload` | Upload a CSV and insert it into the database |
| `GET /datasets` | List all dataset names in the database |
| `GET /datasets/{name}` | Get all rows for one dataset |
| `GET /export` | Download the entire database as a CSV |

---

### `GET /` — Serve the website

Reads `website.html` from disk and sends it to the browser.

---

### `GET /files` — List available CSV files

Returns the names of every `.csv` in the `data/` folder. The website uses this for the file picker dropdown.

```
Request:   GET /files
Response:  ["sample_data.csv", "spring_data.csv", "summer_data.csv"]
```

---

### `GET /files/{name}` — Get a CSV file's contents

Returns the raw CSV text. The website uses this to preview a file before uploading.

```
Request:   GET /files/sample_data.csv
Response:  date,temp_c,humidity
           2026-01-01,3,78
           2026-01-02,1,82
           ...
```

---

### `POST /upload` — Upload a CSV into the database

Takes a CSV file and a dataset name, parses every row, and inserts it into the `weather` table.

```
Request:
  POST /upload
  file = sample_data.csv
  dataset = "winter"

What happens:
  1. FastAPI receives the file
  2. csv.DictReader parses each row
  3. Each row becomes a Weather object
  4. All rows are inserted in one transaction
  5. The transaction is committed

Response:
  {"inserted": 30}
```

```
┌──────────┐       POST /upload        ┌──────────┐       INSERT INTO       ┌──────────┐
│          │  ───────────────────────►  │          │  ──────────────────►   │          │
│ Browser  │     (CSV file + name)     │  Server  │    weather table       │  SQLite  │
│          │  ◄───────────────────────  │          │  ◄──────────────────   │  (.db)   │
│          │    {"inserted": 30}       │          │       done             │          │
└──────────┘                           └──────────┘                        └──────────┘
```

---

### `GET /datasets` — List all dataset names

Returns every unique dataset name. The website uses this to render the tabs.

```
Request:   GET /datasets
SQL:       SELECT DISTINCT dataset FROM weather;
Response:  ["winter", "spring", "summer"]
```

---

### `GET /datasets/{name}` — Get all rows for one dataset

Returns every row for a dataset as JSON, ordered by date. The website uses this to build the table and charts when you click a tab. Each row is converted using `Weather.to_dict()`.

```
Request:   GET /datasets/winter
SQL:       SELECT * FROM weather WHERE dataset = 'winter' ORDER BY date;
Response:  [
             {"date": "2026-01-01", "temp_c": 3.0, "humidity": 78.0},
             {"date": "2026-01-02", "temp_c": 1.0, "humidity": 82.0},
             ...
           ]
```

```
┌──────────┐    GET /datasets/winter    ┌──────────┐    SELECT * FROM      ┌──────────┐
│          │  ───────────────────────►   │          │  ──────────────────►  │          │
│ Browser  │                            │  Server  │    WHERE dataset=     │  SQLite  │
│          │  ◄───────────────────────   │          │  ◄──────────────────  │  (.db)   │
│          │      JSON array            │          │      rows             │          │
└──────────┘                            └──────────┘                       └──────────┘
                      │
                      ▼
              Plotly.js renders
              interactive charts
```

---

### `GET /export` — Download everything as CSV

Returns the entire `weather` table as a downloadable `.csv` file.

```
Request:   GET /export
SQL:       SELECT * FROM weather;
Response:  dataset,date,temp_c,humidity
           winter,2026-01-01,3.0,78.0
           winter,2026-01-02,1.0,82.0
           ...
```

---

## Why the volume matters

The SQLite database lives inside the container at `/app/data/weather.db`. Without a volume, that file disappears when the container is removed. The volume keeps it alive:

```
Without volume:                          With volume:
┌───────────────┐                       ┌───────────────┐
│   Container   │                       │   Container   │
│  /app/data/   │                       │  /app/data/ ──┼──► Docker Volume (dbdata)
│  weather.db   │                       │               │    weather.db lives HERE
└───────────────┘                       └───────────────┘

docker compose down                     docker compose down
  → container deleted                     → container deleted
  → weather.db GONE                       → volume STILL EXISTS
                                          → data survives

docker compose up                       docker compose up
  → empty database                        → same data still there
```

`docker compose down` keeps the volume. `docker compose down -v` wipes it.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Web framework | **FastAPI** | Minimal setup, auto-generates API docs at `/docs` |
| Database | **SQLite** | Zero config, just a file — no separate server needed |
| ORM | **SQLAlchemy** | Maps Python classes to database tables |
| Charts | **Plotly.js** | Interactive charts with hover/zoom/pan out of the box |
| Container | **Docker** | One command to run everything, works on any machine |
