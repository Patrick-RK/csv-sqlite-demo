"""
Database setup and model.

This file defines:
  - How to connect to the SQLite database
  - What the weather table looks like
"""

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
