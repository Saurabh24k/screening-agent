from typing import Dict, List, Optional
from backend.app.models.candidate import Candidate


class MemoryStore:
    """
    In-memory store to simulate database for development.
    Stores candidates by ID and helps check for duplicates.
    """

    def __init__(self):
        self.candidates: Dict[str, Candidate] = {}

    async def save_candidate(self, candidate: Candidate):
        self.candidates[candidate.id] = candidate

    async def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        return self.candidates.get(candidate_id)

    async def find_duplicate_candidates(self, candidate: Candidate) -> List[Candidate]:
        duplicates = []
        for existing in self.candidates.values():
            if (
                existing.email == candidate.email or
                (candidate.phone and existing.phone == candidate.phone) or
                (candidate.resume_hash and existing.resume_hash == candidate.resume_hash)
            ):
                duplicates.append(existing)
        return duplicates
