from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class SearchFilters(BaseModel):
    video_ids: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None


class ClipResult(BaseModel):
    clip_id: str
    video_id: str
    video_title: str
    start_time: float
    end_time: float
    duration: float
    relevance_score: float
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None
    clip_url: Optional[str] = None  # Presigned playback URL
    created_at: datetime


class SearchResponse(BaseModel):
    query: str
    search_id: str
    total_results: int
    clips: List[ClipResult]
    processing_time_ms: float


class SearchHistoryItem(BaseModel):
    search_id: str
    query: str
    results_count: int
    processing_time_ms: float
    created_at: str


class TrackViewRequest(BaseModel):
    clip_id: str
    search_query_id: Optional[str] = None
    duration_seconds: Optional[float] = None
