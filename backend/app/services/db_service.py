# backend/app/services/db_service.py

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv

# 🔧 Load environment variables from backend/.env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Check your .env file and path.")

# 🔌 Database Engine + Session setup
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Base class for SQLAlchemy models
Base = declarative_base()

# ✅ FastAPI-compatible DB dependency
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
