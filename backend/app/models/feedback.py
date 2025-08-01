# backend/app/models/feedback.py

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.app.services.db_service import Base
import uuid

class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(String, ForeignKey("llm_screening_data.candidate_id"), nullable=False)
    interviewer = Column(String, nullable=False)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    status = Column(String, nullable=False)  # hire / hold / drop
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())