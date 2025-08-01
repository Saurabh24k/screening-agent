import hashlib
import re
from typing import Dict, Any, Optional

from backend.app.agents.base import BaseAgent
from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription


class ParsingAgent(BaseAgent):
    """
    Agent responsible for extracting candidate information from a resume
    and calculating similarity to a job description.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ParsingAgent", config=config)

    async def process(self, input_data: Dict[str, Any]) -> Candidate:
        resume_text = input_data.get("resume_text", "")
        job_description = input_data.get("job_description", "")

        # Parse resume fields
        candidate_data = await self._parse_resume(resume_text)
        candidate_data["resume_text"] = resume_text
        candidate_data["resume_hash"] = hashlib.md5(resume_text.encode()).hexdigest()

        # JD Similarity score (dummy for now)
        jd_score = await self._calculate_jd_similarity(resume_text, job_description)
        candidate_data["jd_similarity"] = jd_score

        candidate = Candidate(**candidate_data)
        self.log_info(f"Parsed candidate: {candidate.name}", candidate.id)

        return candidate

    async def _parse_resume(self, resume_text: str) -> Dict[str, Any]:
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        email = emails[0] if emails else "unknown@example.com"

        # Extract phone
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phones = re.findall(phone_pattern, resume_text)
        phone = phones[0] if phones else None

        # Placeholder parsing logic
        return {
            "id": hashlib.md5(email.encode()).hexdigest()[:8],
            "name": "John Doe",  # Hardcoded for now
            "email": email,
            "phone": phone,
            "location": "Unknown",
            "skills": ["Python", "SQL", "Machine Learning"],
            "experience": {"Python": 3, "SQL": 2},
            "education": "Bachelor's in Computer Science",
            "certifications": [],
            "languages": ["English"],
            "notice_period": "Immediate"
        }

    async def _calculate_jd_similarity(self, resume_text: str, job_description: JobDescription) -> float:
        jd_text = job_description.description or ""
        jd_words = set(jd_text.lower().split())
        resume_words = set(resume_text.lower().split())
        overlap = jd_words.intersection(resume_words)
        if not jd_words:
            return 0.0
        return len(overlap) / len(jd_words) * 100

