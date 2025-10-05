from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CompilationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    clip_ids: list[str]

class CompilationResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    clips_count: int
    duration: Optional[float] = None
    created_at: datetime
