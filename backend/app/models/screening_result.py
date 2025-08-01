from typing import Dict, List, Optional
from pydantic import BaseModel


class ScreeningRequest(BaseModel):
    job_id: str
    resume_text: str


class ScreeningResultModel(BaseModel):
    candidate_id: str
    current_org: str
    current_role: str
    validated_skills: Dict[str, bool]
    availability: str
    relocation_intent: bool
    enthusiasm_score: float
    red_flags: List[str]
    notes: str


class MatchScoreModel(BaseModel):
    candidate_id: str
    relevance_score: float
    tier: str  # Can convert enum to str for easier JSON response
    reasoning: str
    red_flags: List[str]
    skill_match_percentage: float


class SchedulingResultModel(BaseModel):
    status: str
    time: str


class ScreeningResponse(BaseModel):
    status: str
    candidate_id: str
    screening_result: ScreeningResultModel
    match_score: MatchScoreModel
    scheduling: SchedulingResultModel

class FeedbackModel(BaseModel):
    candidate_id: str
    interviewer: str
    rating: float  # 1.0–5.0
    status: str  # "hire" | "hold" | "drop"
    notes: Optional[str] = ""