import csv
import io
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data/weather.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

TEMPLATES = Path(__file__).parent / "templates"
DATA_DIR = Path("/app/csvdata")


class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True)
    dataset = Column(String, nullable=False)
    date = Column(String, nullable=False)
    temp_c = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="CSV-Postgres Demo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    return (TEMPLATES / "website.html").read_text()


@app.get("/files")
def list_files():
    if not DATA_DIR.exists():
        return []
    return sorted(f.name for f in DATA_DIR.glob("*.csv"))


@app.get("/files/{name}")
def get_file(name: str):
    path = DATA_DIR / name
    if not path.exists() or not path.suffix == ".csv":
        return {"error": "not found"}
    return StreamingResponse(
        open(path),
        media_type="text/csv",
    )


@app.get("/datasets")
def list_datasets():
    db = SessionLocal()
    rows = db.query(Weather.dataset).distinct().all()
    db.close()
    return [r[0] for r in rows]


@app.get("/datasets/{name}")
def get_dataset(name: str):
    db = SessionLocal()
    rows = db.query(Weather).filter(Weather.dataset == name).order_by(Weather.date).all()
    db.close()
    return [{"date": r.date, "temp_c": r.temp_c, "humidity": r.humidity} for r in rows]


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), dataset: str = Form(...)):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode()))
    db = SessionLocal()
    count = 0
    for row in reader:
        db.add(Weather(
            dataset=dataset,
            date=row["date"],
            temp_c=float(row["temp_c"]),
            humidity=float(row["humidity"]),
        ))
        count += 1
    db.commit()
    db.close()
    return {"inserted": count}


@app.get("/export")
def export_csv():
    db = SessionLocal()
    rows = db.query(Weather).all()
    db.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["dataset", "date", "temp_c", "humidity"])
    for row in rows:
        writer.writerow([row.dataset, row.date, row.temp_c, row.humidity])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"},
    )
