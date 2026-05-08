# CSV → SQLite Demo

A minimal web app that lets you upload CSV files, store them in a SQLite database, and visualise the data with interactive charts.

## What's in the box

```
csv-postgres-demo/
├── docker-compose.yml     # Defines the single container + volume
├── Dockerfile             # Builds the Python app image
├── requirements.txt       # Python dependencies
├── app/
│   ├── server.py          # FastAPI backend (routes + database model)
│   ├── static/
│   │   ├── temperature_chart.js  # Plotly temperature line chart
│   │   └── humidity_chart.js     # Plotly humidity bar chart
│   └── templates/
│       └── website.html   # Frontend (HTML + CSS)
├── data/
│   ├── sample_data.csv    # 30 days of fake winter weather
│   ├── spring_data.csv    # 30 days of fake spring weather
│   └── summer_data.csv    # 30 days of fake summer weather
└── scripts/
    ├── seed_database.py         # Uploads sample.csv into the running app
    └── test_server_endpoints.py # End-to-end test script
```

## How it works — step by step

### Step 1: You run `docker compose up`

Docker reads `docker-compose.yml` and does two things:

1. **Builds an image** from the `Dockerfile` — installs Python + dependencies + your code
2. **Creates a volume** called `dbdata` — a persistent folder that survives container restarts

```
┌─────────────────────────────────────────────┐
│  docker compose up --build                  │
│                                             │
│  1. Read Dockerfile                         │
│  2. Install Python 3.12                     │
│  3. pip install fastapi, sqlalchemy, etc.   │
│  4. Copy app/ into the image                │
│  5. Start uvicorn server on port 8000       │
│  6. Map port 8001 (your machine) → 8000     │
│  7. Mount volume dbdata → /app/data/        │
└─────────────────────────────────────────────┘
```

### Step 2: The app starts up

When the FastAPI app boots, it runs this line:

```python
Base.metadata.create_all(engine)
```

This creates the `weather` table in `/app/data/weather.db` if it doesn't already exist:

```
┌──────────────────────────────────┐
│  weather table                   │
├──────┬─────────┬────────┬────────┤
│  id  │ dataset │  date  │ temp_c │ humidity │
├──────┼─────────┼────────┼────────┤
│  1   │ sample  │ 2026.. │  3.0   │  78.0    │
│  2   │ sample  │ 2026.. │  1.0   │  82.0    │
│ ...  │  ...    │  ...   │  ...   │  ...     │
└──────┴─────────┴────────┴────────┘
```

### Step 3: You open the browser

Go to `http://localhost:8001`. The browser loads `index.html` which gives you:

- A **drop zone** to pick or drag a CSV file
- A **collapsible data table** showing a preview of the CSV
- **Interactive charts** (powered by Plotly.js) — hover, zoom, pan
- **Tabs** to switch between previously uploaded datasets

### Step 4: You upload a CSV

Here's what happens when you click "upload to database":

```
┌──────────┐       POST /upload        ┌──────────┐       INSERT INTO       ┌──────────┐
│          │  ───────────────────────►  │          │  ──────────────────►   │          │
│ Browser  │     (CSV file + name)     │ FastAPI  │    weather table       │  SQLite  │
│          │  ◄───────────────────────  │          │  ◄──────────────────   │  (.db)   │
│          │    {"inserted": 30}       │          │       done             │          │
└──────────┘                           └──────────┘                        └──────────┘
```

1. Browser reads the CSV file and sends it as a `POST` request
2. FastAPI parses each row with Python's `csv.DictReader`
3. SQLAlchemy inserts each row into the `weather` table
4. Response goes back: `{"inserted": 30}`

### Step 5: You view a saved dataset

When you click a tab:

```
┌──────────┐     GET /datasets/sample   ┌──────────┐    SELECT * FROM      ┌──────────┐
│          │  ───────────────────────►   │          │  ──────────────────►  │          │
│ Browser  │                            │ FastAPI  │    WHERE dataset=     │  SQLite  │
│          │  ◄───────────────────────   │          │  ◄──────────────────  │  (.db)   │
│          │      JSON array            │          │      rows             │          │
└──────────┘                            └──────────┘                       └──────────┘
                      │
                      ▼
              Plotly.js renders
              interactive charts
```

## Why the volume matters

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
docker compose up
  → fresh container                     docker compose up
  → empty database                        → new container
                                          → mounts same volume
                                          → data is still there
```

The volume (`dbdata`) is a folder managed by Docker that exists **outside** the container. When the container is deleted and recreated, the volume stays. Your data only gets wiped if you explicitly run `docker compose down -v` (the `-v` flag removes volumes).

## Quick start

```bash
# 1. Start everything
docker compose up --build -d

# 2. Seed it with sample data
pip install requests
python scripts/seed_database.py

# 3. Open the app
open http://localhost:8001

# 4. Run the test to verify everything works
python scripts/test_server_endpoints.py

# 5. Stop (keeps data)
docker compose down

# 6. Stop and wipe data
docker compose down -v
```

## API endpoints

### `GET /` — Serve the web page

Returns the `website.html` file. This is the page you see when you open `http://localhost:8001` in your browser.

```
Browser: GET /
Server:  reads app/templates/website.html from disk
         returns it as HTML
Browser: renders the page
```

---

### `POST /upload` — Upload a CSV into the database

Accepts a CSV file and a dataset name. Parses every row and inserts it into the `weather` table.

**Form fields:**
- `file` — the CSV file (must have columns: `date`, `temp_c`, `humidity`)
- `dataset` — a name to group these rows under (e.g. `"january"`)

```
Request:
  POST /upload
  file=sample.csv
  dataset=january

What happens:
  1. FastAPI receives the file
  2. Python's csv.DictReader parses each row
  3. SQLAlchemy creates a Weather object per row
  4. All rows are inserted into the weather table in one transaction
  5. The transaction is committed

Response:
  {"inserted": 30}
```

---

### `GET /datasets` — List all dataset names

Returns a JSON array of every unique dataset name in the database. This is what populates the tabs in the UI.

```
Request:
  GET /datasets

SQL that runs:
  SELECT DISTINCT dataset FROM weather;

Response:
  ["january", "february", "march"]
```

---

### `GET /datasets/{name}` — Get all rows for one dataset

Returns every row belonging to a dataset, ordered by date. The frontend uses this to build the table and charts when you click a tab.

```
Request:
  GET /datasets/january

SQL that runs:
  SELECT * FROM weather
  WHERE dataset = 'january'
  ORDER BY date;

Response:
  [
    {"date": "2026-01-01", "temp_c": 3.0, "humidity": 78.0},
    {"date": "2026-01-02", "temp_c": 1.0, "humidity": 82.0},
    ...
  ]
```

---

### `GET /export` — Download everything as CSV

Returns the entire `weather` table as a downloadable CSV file. Includes all datasets.

```
Request:
  GET /export

SQL that runs:
  SELECT * FROM weather;

Response (CSV file download):
  dataset,date,temp_c,humidity
  january,2026-01-01,3.0,78.0
  january,2026-01-02,1.0,82.0
  ...
```

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Web framework | **FastAPI** | Minimal setup, auto-generates API docs at `/docs` |
| Database | **SQLite** | Zero config, just a file — no separate server needed |
| ORM | **SQLAlchemy** | Maps Python classes to database tables |
| Charts | **Plotly.js** | Interactive charts with hover/zoom/pan out of the box |
| Container | **Docker** | One command to run everything, works on any machine |
