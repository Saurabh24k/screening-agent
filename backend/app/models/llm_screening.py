# backend/app/models/llm_screening.py

from sqlalchemy import Column, String, Text, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from backend.app.services.db_service import Base
from sqlalchemy.sql import func


class LLM_ScreeningData(Base):
    __tablename__ = "llm_screening_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    reasoning = Column(Text)
    red_flags = Column(ARRAY(Text))
    embedding = Column(Vector(768))
    status = Column(String, default="processed")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
