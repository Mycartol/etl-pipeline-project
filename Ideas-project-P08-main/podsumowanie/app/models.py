from pydantic import BaseModel
from enum import Enum

class AIBackend(str, Enum):
    openai = "openai"
    localai = "localai"

class SummaryResponse(BaseModel):
    summary: str
    mongo_id: str | None = None
