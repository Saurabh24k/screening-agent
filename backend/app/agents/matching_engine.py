from typing import Dict, Any, Optional

from backend.app.agents.base import BaseAgent
from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription
from backend.app.models.screening_result import ScreeningResultModel
from backend.app.models.match_score import MatchScore
from backend.app.models.enums import CandidateTier


class MatchingEngine(BaseAgent):
    """
    Evaluates a candidate against a job using skills, experience, and screening result.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="MatchingEngine", config=config)

    async def process(self, input_data: Dict[str, Any]) -> MatchScore:
        candidate: Candidate = input_data["candidate"]
        job: JobDescription = input_data["job_description"]
        screen: ScreeningResultModel = input_data["screening_result"]

        self.log_info("Calculating match score", candidate.id)

        skill_match = await self._calculate_skill_match(candidate, job)
        experience_match = await self._calculate_experience_match(candidate, job)
        screening_factor = await self._calculate_screening_factor(screen)

        # Weighted scoring
        relevance_score = round(
            (skill_match * 0.4) +
            (experience_match * 0.3) +
            (screening_factor * 0.3),
            2
        )

        tier = self._assign_tier(relevance_score, screen.red_flags)
        reasoning = await self._generate_reasoning(candidate, job, screen, relevance_score)

        result = MatchScore(
            candidate_id=candidate.id,
            relevance_score=relevance_score,
            tier=tier,
            reasoning=reasoning,
            red_flags=screen.red_flags,
            skill_match_percentage=skill_match
        )

        self.log_info(f"Match score: {relevance_score:.1f} → Tier: {tier.value}", candidate.id)
        return result

    async def _calculate_skill_match(self, candidate: Candidate, jd: JobDescription) -> float:
        required = set(skill.lower() for skill in jd.required_skills)
        actual = set(skill.lower() for skill in candidate.skills)

        if not required:
            return 100.0

        matched = required & actual
        return round((len(matched) / len(required)) * 100, 2)

    async def _calculate_experience_match(self, candidate: Candidate, jd: JobDescription) -> float:
        total_years = sum(candidate.experience.values())
        if total_years >= jd.experience_required:
            return 100.0
        return round((total_years / jd.experience_required) * 100, 2)

    async def _calculate_screening_factor(self, screen: ScreeningResultModel) -> float:
        base = screen.enthusiasm_score * 10  # 0–100
        penalty = len(screen.red_flags) * 10
        return max(0, base - penalty)

    async def _generate_reasoning(
        self, candidate: Candidate, jd: JobDescription, screen: ScreeningResultModel, score: float
    ) -> str:
        if score >= 80:
            return f"Excellent fit for {jd.title} — highly motivated and skilled."
        elif score >= 60:
            return f"Good potential, some gaps in skills or enthusiasm."
        else:
            return f"Not a strong fit — concerns in alignment or red flags."

    def _assign_tier(self, score: float, red_flags: list) -> CandidateTier:
        if red_flags and len(red_flags) > 2:
            return CandidateTier.C
        if score >= 80:
            return CandidateTier.A
        elif score >= 60:
            return CandidateTier.B
        return CandidateTier.C
