# backend/app/services/llm_log_service.py

from backend.app.models.llm_screening import LLM_ScreeningData
from sqlalchemy.orm import Session
from uuid import uuid4

def save_llm_screening_record(
    db: Session,
    candidate_id: str,
    job_id: str,
    reasoning: str,
    red_flags: list[str],
    embedding: list[float]
):
    record = LLM_ScreeningData(
        id=uuid4(),
        candidate_id=candidate_id,
        job_id=job_id,
        reasoning=reasoning,
        red_flags=red_flags,
        embedding=embedding,  # pgvector field expects list[float]
        status="processed"
        # created_at is auto-filled by DB default
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
