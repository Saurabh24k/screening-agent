from fastapi import APIRouter, HTTPException, Depends
from dataclasses import asdict
from sqlalchemy.orm import Session

from backend.app.models.screening_result import ScreeningRequest, ScreeningResponse
from backend.app.models.job_description import JobDescription
from backend.app.models.match_score import MatchScoreModel
from backend.app.models.scheduling import SchedulingResultModel
from backend.app.models.screening_result import ScreeningResultModel

from backend.app.core.aisystem import get_orchestrator
from backend.app.services.db_service import get_db
from backend.app.services.llm_log_service import save_llm_screening_record
from backend.app.utils.embedding import get_embedding

# 🧠 Memory stores used by similarity API
from backend.app.api.routes.candidates import CANDIDATE_DB
from backend.app.api.routes.jobs import JOBS_DB

router = APIRouter()

# ✅ Temporary dummy job store (replace with DB later)
DUMMY_JOBS = {
    "job123": JobDescription(
        id="job123",
        title="ML Engineer",
        company="Syna",
        description="Looking for a skilled ML Engineer with Python, SQL, AWS",
        required_skills=["Python", "SQL", "AWS"],
        preferred_skills=["Docker", "LangChain"],
        experience_required=2,
        location="Remote"
    )
}

@router.post("/screen", response_model=ScreeningResponse)
async def screen_candidate(payload: ScreeningRequest, db: Session = Depends(get_db)):
    job = DUMMY_JOBS.get(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    orchestrator = get_orchestrator()

    result = await orchestrator.process({
        "resume_text": payload.resume_text,
        "job_description": job,
    })

    if result["status"] != "processed":
        raise HTTPException(status_code=400, detail=result.get("reason", "Processing failed"))

    # ✨ Generate real embedding from reasoning text
    reasoning_text = result["match_score"].reasoning
    embedding = get_embedding(reasoning_text)

    # 🧠 Save to PostgreSQL (LLM log)
    save_llm_screening_record(
        db=db,
        candidate_id=result["candidate_id"],
        job_id=payload.job_id,
        reasoning=reasoning_text,
        red_flags=result["match_score"].red_flags,
        embedding=embedding,
    )

    # 🗃️ Cache for metadata enrichment in /similar endpoint
    CANDIDATE_DB[result["candidate_id"]] = {
        "name": "John Doe",  # (you can update dynamically later)
        "skills": list(result["screening_result"].validated_skills.keys()),
        "job_id": payload.job_id,  # 🔥 This is critical
        "enthusiasm_score": result["screening_result"].enthusiasm_score,
        "availability": result["screening_result"].availability,
        "relocation": result["screening_result"].relocation_intent,
    }
    
    JOBS_DB[payload.job_id] = job  # Ensure job is also cached

    # 🧼 Serialize dataclass or model safely
    def serialize_model(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        return obj

    return ScreeningResponse(
        status="processed",
        candidate_id=result["candidate_id"],
        screening_result=serialize_model(result["screening_result"]),
        match_score=serialize_model(result["match_score"]),
        scheduling=serialize_model(result["scheduling"]),
    )
