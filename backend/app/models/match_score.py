from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel
from backend.app.models.enums import CandidateTier


# ✅ Internal use in agents
@dataclass
class MatchScore:
    candidate_id: str
    relevance_score: float  # 0–100
    tier: CandidateTier
    reasoning: str
    red_flags: List[str] = field(default_factory=list)
    skill_match_percentage: float = 0.0


# ✅ For API responses
class MatchScoreModel(BaseModel):
    candidate_id: str
    relevance_score: float
    tier: str  # converted from enum to string
    reasoning: str
    red_flags: List[str]
    skill_match_percentage: float
