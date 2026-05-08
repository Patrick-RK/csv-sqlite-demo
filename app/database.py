"""
Database setup and model.

This file defines:
  - How to connect to the SQLite database
  - What the weather table looks like
  - A helper to get a database session
"""

from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data/weather.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True)
    dataset = Column(String, nullable=False)
    date = Column(String, nullable=False)
    temp_c = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)

    def to_dict(self):
        return {"date": self.date, "temp_c": self.temp_c, "humidity": self.humidity}


@contextmanager
def get_db():
    """Open a database session, then close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
