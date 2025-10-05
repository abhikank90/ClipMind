from fastapi import APIRouter
from app.api.v1.endpoints import videos, search, compilations, analytics

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(compilations.router, prefix="/compilations", tags=["compilations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
