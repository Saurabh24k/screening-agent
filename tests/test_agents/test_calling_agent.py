import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.calling_agent import CallingAgent
from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription


async def run_test():
    agent = CallingAgent()

    candidate = Candidate(
        id="cand123",
        name="John Doe",
        email="john@example.com",
        phone="555-123-4567",
        location="NY",
        skills=["Python", "AWS", "SQL"],
        experience={"Python": 3, "AWS": 2},
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
        experience_required=3,
        location="Remote",
        description="Looking for a Python + SQL backend engineer.",
        salary_range="$100K - $130K"
    )

    result = await agent.process({
        "candidate": candidate,
        "job_description": jd,
        "mode": "chat"
    })

    print("✅ Screening Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(run_test())
