import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.uniqueness_verifier import UniquenessVerifier
from backend.app.models.candidate import Candidate
from backend.app.core.memory_store import MemoryStore


async def run_test():
    store = MemoryStore()
    agent = UniquenessVerifier(memory_store=store)

    # Candidate 1
    c1 = Candidate(
        id="abc123",
        name="John Doe",
        email="john@example.com",
        phone="555-123-4567",
        location="SF",
        skills=["Python"],
        experience={"Python": 3},
        education="BS CS",
        certifications=[],
        languages=["English"],
        notice_period="Immediate",
        resume_text="...",
        resume_hash="hash123",
        jd_similarity=90.0
    )

    await store.save_candidate(c1)

    # Candidate 2 (duplicate email)
    c2 = Candidate(
        id="xyz789",
        name="Jane Smith",
        email="john@example.com",  # same email
        phone="555-000-0000",
        location="NY",
        skills=["SQL"],
        experience={"SQL": 2},
        education="BS IT",
        certifications=[],
        languages=["English"],
        notice_period="2 weeks",
        resume_text="...",
        resume_hash="diffhash",
        jd_similarity=75.0
    )

    result = await agent.process(c2)
    print("✅ Duplicate Check Result:", result)


if __name__ == "__main__":
    asyncio.run(run_test())
