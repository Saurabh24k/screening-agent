from pydantic import BaseModel
from typing import List, Optional

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    experience_required: int
    location: str

class JobDescription(JobCreate):
    id: str
    salary_range: Optional[str] = None
