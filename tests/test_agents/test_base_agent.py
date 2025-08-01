import sys
import os
import asyncio

# Fix: Add this before using sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.agents.base import BaseAgent

class DummyAgent(BaseAgent):
    async def process(self, input_data):
        self.log_info("Processing input data...", candidate_id=input_data.get("candidate_id"))
        return {"status": "success", "data": input_data}

# Async test runner
async def run_test():
    agent = DummyAgent(name="DummyAgent")
    result = await agent.process({"candidate_id": "abc123", "message": "Hello world"})
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(run_test())
