import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.scheduling_agent import SchedulingAgent
from backend.app.models.candidate import Candidate
from backend.app.models.match_score import MatchScore
from backend.app.models.enums import CandidateTier


async def run_test():
    agent = SchedulingAgent()

    candidate = Candidate(
        id="cand123",
        name="John Doe",
        email="john@example.com",
        phone="555-123-4567",
        location="NY",
        skills=["Python", "SQL"],
        experience={"Python": 3, "SQL": 2},
        education="BS CS",
        certifications=[],
        languages=["English"],
        notice_period="Immediate",
        resume_text="...",
        resume_hash="hashabc",
        jd_similarity=85.0
    )

    match = MatchScore(
        candidate_id="cand123",
        relevance_score=91.0,
        tier=CandidateTier.A,
        reasoning="Excellent fit for the job.",
        red_flags=[],
        skill_match_percentage=100.0
    )

    result = await agent.process({
        "candidate": candidate,
        "match_score": match
    })

    print("✅ Scheduling Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(run_test())
