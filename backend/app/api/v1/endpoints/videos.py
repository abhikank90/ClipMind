from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
import logging
import time

from app.schemas.video import VideoResponse, VideoUploadResponse
from app.services.video_service import VideoService
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Query(default="Untitled"),
    current_user: dict = Depends(get_current_user)
):
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    service = VideoService()
    result = await service.upload_video(file, title, current_user["id"])
    
    return VideoUploadResponse(
        video_id=result["video_id"],
        filename=result["filename"],
        title=title,
        status="processing",
        message="Video uploaded successfully"
    )

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, current_user: dict = Depends(get_current_user)):
    service = VideoService()
    video = await service.get_video(video_id, current_user["id"])
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.get("/", response_model=list[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    service = VideoService()
    videos = await service.list_videos(current_user["id"], skip, limit)
    return videos

@router.delete("/{video_id}")
async def delete_video(video_id: str, current_user: dict = Depends(get_current_user)):
    service = VideoService()
    success = await service.delete_video(video_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": f"Video {video_id} deleted"}
