from pydantic import BaseModel


class SchedulingResultModel(BaseModel):
    status: str
    time: str
