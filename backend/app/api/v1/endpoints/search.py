from fastapi import APIRouter, HTTPException, Depends, Query
import logging

from app.schemas.search import SearchResponse
from app.services.search_service import SearchService
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=SearchResponse)
async def search_videos(
    query: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    service = SearchService()
    results = await service.search(query, current_user["id"], limit)
    return results

@router.get("/similar/{clip_id}")
async def find_similar_clips(
    clip_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    service = SearchService()
    results = await service.find_similar(clip_id, current_user["id"], limit)
    return results
