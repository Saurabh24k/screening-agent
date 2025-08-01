import asyncio
from typing import Dict, Any, Optional

from backend.app.agents.base import BaseAgent
from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription
from backend.app.models.screening_result import ScreeningResultModel


class CallingAgent(BaseAgent):
    """
    Simulates a screening interview with the candidate.
    Can run in 'chat' or 'voice' mode (mocked).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="CallingAgent", config=config)

    async def process(self, input_data: Dict[str, Any]) -> ScreeningResultModel:
        candidate: Candidate = input_data["candidate"]
        job: JobDescription = input_data["job_description"]
        mode = input_data.get("mode", "chat")

        self.log_info(f"Starting {mode} screening", candidate.id)

        if mode == "voice":
            result = await self._simulate_voice_screening(candidate, job)
        else:
            result = await self._simulate_chat_screening(candidate, job)

        self.log_info("Screening completed", candidate.id)
        return result

    async def _simulate_chat_screening(self, candidate: Candidate, job: JobDescription) -> ScreeningResultModel:
        await asyncio.sleep(0.5)  # Simulate async conversation delay

        return ScreeningResultModel(
            candidate_id=candidate.id,
            current_org="TechCorp Inc",
            current_role="ML Engineer",
            validated_skills={skill: True for skill in candidate.skills},
            availability="Immediate",
            relocation_intent=False,
            enthusiasm_score=7.5,
            red_flags=["Expected salary higher than budget"],
            notes="Strong technical skills, motivated but cost might be a blocker."
        )

    async def _simulate_voice_screening(self, candidate: Candidate, job: JobDescription) -> ScreeningResultModel:
        await asyncio.sleep(1.0)  # Longer delay for voice simulation

        return ScreeningResultModel(
            candidate_id=candidate.id,
            current_org="Initech Ltd",
            current_role="Senior Developer",
            validated_skills={skill: True for skill in candidate.skills[:2]},
            availability="2 weeks",
            relocation_intent=True,
            enthusiasm_score=8.2,
            red_flags=[],
            notes="Highly confident and clearly experienced in required stack."
        )
