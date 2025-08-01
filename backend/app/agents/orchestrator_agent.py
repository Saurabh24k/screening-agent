from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.agents.parsing_agent import ParsingAgent
from backend.app.agents.uniqueness_verifier import UniquenessVerifier
from backend.app.agents.calling_agent import CallingAgent
from backend.app.agents.matching_engine import MatchingEngine
from backend.app.agents.scheduling_agent import SchedulingAgent
from backend.app.models.job_description import JobDescription
from backend.app.core.memory_store import MemoryStore


class OrchestratorAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="OrchestratorAgent", config=config)

        memory = MemoryStore()

        self.parser = ParsingAgent()
        self.duplicate_checker = UniquenessVerifier(memory_store=memory)
        self.screening_agent = CallingAgent()
        self.matching_engine = MatchingEngine()
        self.scheduling_agent = SchedulingAgent()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        job: JobDescription = input_data["job_description"]
        resume_text: str = input_data["resume_text"]

        # Step 1: Parse candidate
        candidate = await self.parser.process({
            "resume_text": resume_text,
            "job_description": job
        })

        # Step 2: Check for duplicates
        duplicate_check = await self.duplicate_checker.process(candidate)
        if duplicate_check["is_duplicate"]:
            self.log_info("Duplicate candidate detected - skipping", candidate.id)
            return {
                "status": "rejected",
                "reason": "duplicate"
            }

        # Step 3: Screen candidate
        screen_result = await self.screening_agent.process({
            "candidate": candidate,
            "job_description": job
        })

        # Step 4: Match candidate
        match_score = await self.matching_engine.process({
            "candidate": candidate,
            "job_description": job,
            "screening_result": screen_result
        })

        # Step 5: Schedule interview
        scheduling_result = await self.scheduling_agent.process({
            "candidate": candidate,
            "match_score": match_score
        })

        return {
            "status": "processed",
            "candidate_id": candidate.id,
            "match_score": match_score,
            "screening_result": screen_result,
            "scheduling": scheduling_result
        }
