# backend/app/api/routes/feedback.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Literal
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.app.services.db_service import get_db
from backend.app.api.routes.candidates import CANDIDATE_DB

router = APIRouter()

class FeedbackModel(BaseModel):
    candidate_id: str
    interviewer: str
    rating: float  # 1.0–5.0
    status: Literal["Hire", "Hold", "Drop"]
    notes: str = ""

# --- POST feedback to DB ---
@router.post("/feedback/{candidate_id}", response_model=FeedbackModel)
async def submit_feedback(candidate_id: str, feedback: FeedbackModel, db: Session = Depends(get_db)):
    query = text("""
        INSERT INTO interview_feedback (candidate_id, interviewer, rating, status, notes)
        VALUES (:candidate_id, :interviewer, :rating, :status, :notes)
    """)
    db.execute(query, feedback.dict())
    db.commit()
    return feedback

# --- GET all feedback for a candidate ---
@router.get("/feedback/{candidate_id}", response_model=List[FeedbackModel])
async def get_feedback(candidate_id: str, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT candidate_id, interviewer, rating, status, notes
        FROM interview_feedback
        WHERE candidate_id = :candidate_id
        ORDER BY created_at DESC
    """), {"candidate_id": candidate_id}).fetchall()
    return [dict(row) for row in result]

# --- GET feedback by job ID ---
@router.get("/feedback/job/{job_id}", response_model=List[FeedbackModel])
async def get_feedback_by_job(job_id: str, db: Session = Depends(get_db)):
    candidate_ids = [cid for cid, cand in CANDIDATE_DB.items() if cand.get("job_id") == job_id]
    if not candidate_ids:
        return []
    query = text("""
        SELECT candidate_id, interviewer, rating, status, notes
        FROM interview_feedback
        WHERE candidate_id = ANY(:candidate_ids)
        ORDER BY created_at DESC
    """)
    result = db.execute(query, {"candidate_ids": candidate_ids}).fetchall()
    return [dict(row) for row in result]

# --- GET summary by job ---
@router.get("/feedback/summary/{job_id}")
async def get_feedback_summary(job_id: str, db: Session = Depends(get_db)):
    candidate_ids = [cid for cid, cand in CANDIDATE_DB.items() if cand.get("job_id") == job_id]
    if not candidate_ids:
        raise HTTPException(status_code=404, detail="No candidates found for job")

    query = text("""
        SELECT rating, status, notes
        FROM interview_feedback
        WHERE candidate_id = ANY(:candidate_ids)
    """)
    result = db.execute(query, {"candidate_ids": candidate_ids}).fetchall()

    if not result:
        return {"job_id": job_id, "average_rating": 0, "decision_breakdown": {}, "highlights": []}

    ratings = [row.rating for row in result]
    breakdown = {"Hire": 0, "Hold": 0, "Drop": 0}
    notes = []

    for row in result:
        normalized_status = row.status.capitalize()
        if normalized_status in breakdown:
            breakdown[normalized_status] += 1
        else:
            breakdown[normalized_status] = 1  # fallback if status is unexpected
        if row.notes:
            notes.append(row.notes)

    return {
        "job_id": job_id,
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "decision_breakdown": breakdown,
        "highlights": notes[:5]  # Top 5 feedback notes
    }
