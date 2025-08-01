from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.models.candidate import Candidate
from backend.app.models.match_score import MatchScore
from backend.app.models.enums import CandidateTier
from backend.app.services.calendar_service import CalendarService


class SchedulingAgent(BaseAgent):
    """
    Decides if a candidate should be scheduled and books time using calendar service.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="SchedulingAgent", config=config)
        self.calendar = CalendarService()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate: Candidate = input_data["candidate"]
        match: MatchScore = input_data["match_score"]

        if match.tier == CandidateTier.C:
            self.log_info("Tier C candidate — skipping scheduling", candidate.id)
            return {
                "status": "skipped",
                "reason": "Low match score or red flags"
            }

        scheduled_time = self.calendar.schedule_interview(candidate.id)
        self.log_info(f"Interview scheduled at {scheduled_time}", candidate.id)

        return {
            "status": "scheduled",
            "time": scheduled_time
        }
