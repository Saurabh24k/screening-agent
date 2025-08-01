from enum import Enum


class CandidateTier(Enum):
    A = "auto-schedule"
    B = "optional"
    C = "reject"
