from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter()

# --- In-memory candidate DB ---
CANDIDATE_DB: Dict[str, "CandidateModel"] = {}

# --- Candidate Model ---
class CandidateModel(BaseModel):
    id: str
    name: str
    email: str
    job_id: str
    resume_text: str
    skills: List[str]
    status: str = "screened"  # screened / interviewed / hired / rejected

# --- GET all candidates ---
@router.get("/candidates", response_model=List[CandidateModel])
async def list_candidates():
    return list(CANDIDATE_DB.values())

# --- GET single candidate by ID ---
@router.get("/candidates/{candidate_id}", response_model=CandidateModel)
async def get_candidate(candidate_id: str):
    candidate = CANDIDATE_DB.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

# --- POST candidate (for testing or manual insert) ---
@router.post("/candidates", response_model=CandidateModel)
async def save_candidate(candidate: CandidateModel):
    candidate.id = candidate.id or str(uuid4())
    CANDIDATE_DB[candidate.id] = candidate
    return candidate

@router.get("/debug/candidates")
async def debug_candidates():
    return CANDIDATE_DB
