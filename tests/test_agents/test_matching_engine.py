import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.matching_engine import MatchingEngine
from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription
from backend.app.models.screening_result import ScreeningResult


async def run_test():
    agent = MatchingEngine()

    candidate = Candidate(
        id="cand123",
        name="John Doe",
        email="john@example.com",
        phone="555-123-4567",
        location="NY",
        skills=["Python", "AWS", "SQL"],
        experience={"Python": 3, "SQL": 2},
        education="BS CS",
        certifications=[],
        languages=["English"],
        notice_period="Immediate",
        resume_text="...",
        resume_hash="hashabc",
        jd_similarity=87.0
    )

    jd = JobDescription(
        id="job001",
        title="Data Engineer",
        company="TechCorp",
        required_skills=["Python", "SQL", "AWS"],
        preferred_skills=["Spark"],
        experience_required=4,
        location="Remote",
        description="Looking for a Python + SQL backend engineer.",
        salary_range="$100K - $130K"
    )

    screen = ScreeningResult(
        candidate_id="cand123",
        current_org="TechCorp",
        current_role="ML Engineer",
        validated_skills={"Python": True, "SQL": True},
        availability="Immediate",
        relocation_intent=False,
        enthusiasm_score=7.0,
        red_flags=[],
        notes="Seems capable"
    )

    result = await agent.process({
        "candidate": candidate,
        "job_description": jd,
        "screening_result": screen
    })

    print("✅ Match Score:")
    print(result)


if __name__ == "__main__":
    asyncio.run(run_test())
