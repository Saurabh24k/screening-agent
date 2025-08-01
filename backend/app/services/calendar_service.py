from datetime import datetime, timedelta
import random


class CalendarService:
    def __init__(self):
        self.booked_slots = []

    def schedule_interview(self, candidate_id: str) -> str:
        now = datetime.now()
        proposed_slot = now + timedelta(days=random.randint(1, 5), hours=random.randint(9, 16))
        slot_str = proposed_slot.strftime("%Y-%m-%d %I:%M %p")
        self.booked_slots.append((candidate_id, slot_str))
        return slot_str
