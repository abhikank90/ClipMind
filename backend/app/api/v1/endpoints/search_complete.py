from fastapi import APIRouter, HTTPException, Depends, Query
import logging

from app.schemas.search_complete import (
    SearchResponse,
    SearchFilters,
    SearchHistoryItem,
    TrackViewRequest
)
from app.services.search_service_complete import SearchService
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SearchResponse)
async def search_videos(
    query: str,
    limit: int = 20,
    video_ids: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Search videos using natural language
    
    Returns enriched results with:
    - Real video titles from database
    - Presigned S3 URLs for thumbnails
    - Presigned playback URLs for clips
    - Complete transcripts
    - Analytics tracking
    """
    filters = None
    if video_ids:
        filters = SearchFilters(video_ids=video_ids)
    
    service = SearchService()
    results = await service.search(query, current_user["id"], filters, limit)
    return results


@router.get("/history", response_model=List[SearchHistoryItem])
async def get_search_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user's search history"""
    service = SearchService()
    history = await service.get_search_history(current_user["id"], limit)
    return history


@router.post("/track-view")
async def track_clip_view(
    request: TrackViewRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Track when user views a clip
    
    Call this endpoint when:
    - User clicks on a search result
    - User starts playing a clip
    - User watches a clip for X seconds
    """
    service = SearchService()
    success = await service.track_clip_view(
        user_id=current_user["id"],
        clip_id=request.clip_id,
        search_query_id=request.search_query_id,
        duration_seconds=request.duration_seconds
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to track view")
    
    return {"status": "tracked", "clip_id": request.clip_id}


@router.get("/analytics/popular-clips")
async def get_popular_clips(
    days: int = 7,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's most viewed clips in last N days"""
    from app.repositories.search_repository import SearchRepository
    from app.db.session import get_db
    
    db = next(get_db())
    try:
        search_repo = SearchRepository(db)
        popular = search_repo.get_popular_clips(
            current_user["id"],
            days=days,
            limit=limit
        )
        return {"popular_clips": popular}
    finally:
        db.close()
