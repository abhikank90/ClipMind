from pydantic import BaseModel

class AnalyticsStats(BaseModel):
    total_videos: int
    total_hours: float
    searches_today: int
    compilations: int
