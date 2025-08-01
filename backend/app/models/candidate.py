from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Candidate:
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    location: str = ""
    skills: List[str] = field(default_factory=list)
    experience: Dict[str, int] = field(default_factory=dict)
    education: str = ""
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    notice_period: Optional[str] = None
    resume_text: str = ""
    resume_hash: str = ""
    jd_similarity: float = 0.0
