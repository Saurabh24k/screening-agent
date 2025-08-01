from fastapi import APIRouter, HTTPException
from typing import List
from backend.app.models.job_description import JobCreate, JobDescription
import uuid

router = APIRouter()

# Dummy in-memory job store
JOBS_DB = {}

@router.get("/jobs", response_model=List[JobDescription])
async def list_jobs():
    return list(JOBS_DB.values())

@router.post("/jobs", response_model=JobDescription)
async def create_job(job_data: JobCreate):
    job_id = str(uuid.uuid4())
    job = JobDescription(id=job_id, **job_data.dict())
    JOBS_DB[job_id] = job
    return job

@router.get("/jobs/{job_id}", response_model=JobDescription)
async def get_job(job_id: str):
    job = JOBS_DB.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/jobs/{job_id}", response_model=dict)
async def delete_job(job_id: str):
    if job_id not in JOBS_DB:
        raise HTTPException(status_code=404, detail="Job not found")
    del JOBS_DB[job_id]
    return {"status": "deleted", "job_id": job_id}
