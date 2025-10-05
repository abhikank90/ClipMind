from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class VideoBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class VideoResponse(VideoBase):
    id: str
    filename: str
    duration: Optional[float] = None
    status: str
    thumbnail_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    title: str
    status: str
    message: str
