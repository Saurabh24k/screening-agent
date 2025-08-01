from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.core.memory_store import MemoryStore
from backend.app.models.candidate import Candidate


class UniquenessVerifier(BaseAgent):
    """
    Checks if a candidate already exists in the system
    using email, phone, or resume hash.
    """

    def __init__(self, memory_store: MemoryStore, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="UniquenessVerifier", config=config)
        self.memory_store = memory_store

    async def process(self, candidate: Candidate) -> Dict[str, Any]:
        duplicates = await self.memory_store.find_duplicate_candidates(candidate)

        if duplicates:
            self.log_info(f"Found {len(duplicates)} potential duplicates", candidate.id)
            return {
                "is_duplicate": True,
                "duplicates": [d.id for d in duplicates],
                "action": "skip_or_merge"
            }

        self.log_info("No duplicates found — candidate is unique", candidate.id)
        return {
            "is_duplicate": False,
            "duplicates": [],
            "action": "proceed"
        }
