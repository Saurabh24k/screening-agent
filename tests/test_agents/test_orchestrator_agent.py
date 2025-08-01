import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.orchestrator_agent import OrchestratorAgent
from backend.app.models.job_description import JobDescription


async def run_test():
    agent = OrchestratorAgent()

    job = JobDescription(
        id="job001",
        title="Data Engineer",
        company="TechCorp",
        required_skills=["Python", "SQL", "AWS"],
        preferred_skills=["Spark"],
        experience_required=3,
        location="Remote",
        description="Looking for a backend engineer with Python + SQL.",
        salary_range="$100K - $130K"
    )

    resume_text = """
    John Doe
    Email: johndoe@example.com
    Phone: 555-123-4567
    Skills: Python, SQL, AWS, Docker
    Experience: 3 years Python, 2 years SQL
    """

    result = await agent.process({
        "job_description": job,
        "resume_text": resume_text
    })

    print("✅ Full Pipeline Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(run_test())
