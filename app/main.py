import csv
import io
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

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
