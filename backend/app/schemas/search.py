from typing import List, Optional
from pydantic import BaseModel

class ClipResult(BaseModel):
    clip_id: str
    video_id: str
    video_title: str
    start_time: float
    end_time: float
    relevance_score: float
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    clips: List[ClipResult]
    processing_time_ms: float
