import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.parsing_agent import ParsingAgent

async def run_test():
    agent = ParsingAgent()
    result = await agent.process({
        "resume_text": """
            John Doe
            Email: johndoe@example.com
            Phone: 555-123-4567
            Skills: Python, SQL, Machine Learning
        """,
        "job_description": "We are hiring for a Python and Machine Learning role."
    })

    print("✅ Candidate Parsed:")
    print(f"ID: {result.id}")
    print(f"Email: {result.email}")
    print(f"Phone: {result.phone}")
    print(f"Skills: {result.skills}")
    print(f"JD Similarity: {result.jd_similarity}%")

if __name__ == "__main__":
    asyncio.run(run_test())
