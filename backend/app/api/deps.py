# backend/app/api/deps.py

from backend.app.services.db import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
