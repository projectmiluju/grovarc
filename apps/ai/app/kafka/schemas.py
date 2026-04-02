from pydantic import BaseModel


class WorkLogSavedEvent(BaseModel):
    workLogId: str
    userId: str
    logDate: str  # ISO date: "2026-04-03"
