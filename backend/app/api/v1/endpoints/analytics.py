from fastapi import APIRouter, Depends

from app.schemas.analytics import AnalyticsStats
from app.services.analytics_service import AnalyticsService
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/stats", response_model=AnalyticsStats)
async def get_analytics_stats(current_user: dict = Depends(get_current_user)):
    service = AnalyticsService()
    stats = await service.get_stats(current_user["id"])
    return stats

@router.get("/activity")
async def get_recent_activity(limit: int = 10, current_user: dict = Depends(get_current_user)):
    service = AnalyticsService()
    activity = await service.get_recent_activity(current_user["id"], limit)
    return activity
