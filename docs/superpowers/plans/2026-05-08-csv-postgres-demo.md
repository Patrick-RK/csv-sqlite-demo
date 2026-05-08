# CSV-Postgres Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A minimal FastAPI app that uploads a CSV into Postgres and exports it back, running entirely in Docker Compose.

**Architecture:** Docker Compose runs two services: a Postgres container and a FastAPI app container. The app has two endpoints — POST to upload CSV, GET to export CSV. One table with one column.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, psycopg2, Docker, Docker Compose

---

## File Structure

```
csv-postgres-demo/
  docker-compose.yml      # Postgres + app services
  Dockerfile              # Python app image
  requirements.txt        # FastAPI, SQLAlchemy, psycopg2, python-multipart, uvicorn
  app/
    main.py               # FastAPI app with endpoints and DB setup
  sample.csv              # One column, one row demo file
```

---

### Task 1: Project scaffold and Docker setup

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `requirements.txt`
- Create: `sample.csv`

- [ ] **Step 1: Create `requirements.txt`**

```
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
python-multipart==0.0.12
```

- [ ] **Step 2: Create `Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Create `docker-compose.yml`**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: demo
      POSTGRES_DB: demo
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://demo:demo@db:5432/demo

volumes:
  pgdata:
```

- [ ] **Step 4: Create `sample.csv`**

```csv
value
hello
```

- [ ] **Step 5: Initialize git repo and commit**

```bash
cd /Users/Pato/Dev/Languages/Python/csv-postgres-demo
git init
git add docker-compose.yml Dockerfile requirements.txt sample.csv
git commit -m "chore: add Docker setup and sample CSV"
```

---

### Task 2: FastAPI app with upload and export endpoints

**Files:**
- Create: `app/main.py`

- [ ] **Step 1: Create `app/main.py`**

```python
import csv
import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://demo:demo@localhost:5432/demo"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="CSV-Postgres Demo", lifespan=lifespan)


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode()))
    db = SessionLocal()
    count = 0
    for row in reader:
        db.add(Data(value=row["value"]))
        count += 1
    db.commit()
    db.close()
    return {"inserted": count}


@app.get("/export")
def export_csv():
    db = SessionLocal()
    rows = db.query(Data).all()
    db.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "value"])
    for row in rows:
        writer.writerow([row.id, row.value])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"},
    )
```

- [ ] **Step 2: Commit**

```bash
git add app/main.py
git commit -m "feat: add FastAPI app with CSV upload and export endpoints"
```

---

### Task 3: Smoke test with Docker Compose

- [ ] **Step 1: Build and start**

```bash
cd /Users/Pato/Dev/Languages/Python/csv-postgres-demo
docker compose up --build -d
```

Wait a few seconds for Postgres to be ready.

- [ ] **Step 2: Upload the sample CSV**

```bash
curl -X POST http://localhost:8000/upload -F "file=@sample.csv"
```

Expected output: `{"inserted":1}`

- [ ] **Step 3: Export from Postgres as CSV**

```bash
curl http://localhost:8000/export
```

Expected output:
```
id,value
1,hello
```

- [ ] **Step 4: Check the auto-generated docs**

Open `http://localhost:8000/docs` in a browser — FastAPI's Swagger UI lets you try both endpoints interactively.

- [ ] **Step 5: Verify data is in Postgres directly**

```bash
docker compose exec db psql -U demo -d demo -c "SELECT * FROM data;"
```

Expected:
```
 id | value
----+-------
  1 | hello
```

- [ ] **Step 6: Stop containers**

```bash
docker compose down
```
