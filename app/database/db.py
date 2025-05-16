from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SQLite URL - используем SQLite вместо MySQL для упрощения
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/tictactoe.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def init_db():
    from app.models.models import Base
    Base.metadata.create_all(bind=engine) 