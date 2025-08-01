# backend/app/api/routes/similarity.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.app.services.db_service import get_db
from backend.app.models.llm_screening import LLM_ScreeningData
from backend.app.api.routes.candidates import CANDIDATE_DB
from backend.app.api.routes.jobs import JOBS_DB
from backend.app.utils.embedding import get_embedding
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class SimilarityRequest(BaseModel):
    query: str
    job_id: Optional[str] = None
    top_k: int = 5

from pgvector import Vector as PgVector  # 👈 Add this
@router.post("/screening/similar")
async def find_similar_screenings(
    request: SimilarityRequest,
    db: Session = Depends(get_db)
):
    query_vector = get_embedding(request.query)

    sql = """
        SELECT id, candidate_id, job_id, reasoning, red_flags, status, created_at,
               embedding <-> CAST(:query_vector AS vector) AS similarity
        FROM llm_screening_data
    """

    if request.job_id:
        sql += " WHERE job_id = :job_id"

    sql += " ORDER BY similarity ASC LIMIT :limit"

    params = {
        "query_vector": query_vector,  # ← plain list[float], not PgVector
        "limit": request.top_k
    }
    if request.job_id:
        params["job_id"] = request.job_id

    results = db.execute(text(sql), params).fetchall()

    enriched = []
    for row in results:
        cand = CANDIDATE_DB.get(row.candidate_id)
        job = JOBS_DB.get(row.job_id)
        enriched.append({
            "candidate_id": row.candidate_id,
            "reasoning": row.reasoning,
            "red_flags": row.red_flags,
            "similarity": row.similarity,
            "candidate_meta": cand,
            "job_meta": job,
            "screened_at": row.created_at
        })

    return enriched
