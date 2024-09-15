# app/api/video_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.video import VideoCreate, VideoOut, VideoUpdate
from crud.crud_video import get_videos, get_video, create_video, update_video, delete_video
from services.youtube_service import YouTubeService

router = APIRouter()

@router.get("/", response_model=list[VideoOut])
async def read_videos(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    videos = await get_videos(db, skip=skip, limit=limit)
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found")
    return videos

@router.get("/{video_id}", response_model=VideoOut)
async def read_video(video_id: int, db: AsyncSession = Depends(get_db)):
    video = await get_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.post("/", response_model=VideoOut)
async def create_new_video(video: VideoCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_video = await create_video(db, video)
        return new_video
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{video_id}", response_model=VideoOut)
async def update_existing_video(video_id: int, video_update: VideoUpdate, db: AsyncSession = Depends(get_db)):
    video = await get_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    updated_video = await update_video(db, video, video_update)
    return updated_video

@router.delete("/{video_id}", response_model=VideoOut)
async def delete_existing_video(video_id: int, db: AsyncSession = Depends(get_db)):
    video = await get_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    deleted_video = await delete_video(db, video_id)
    return deleted_video

@router.get("/state")
async def get_system_state(session: AsyncSession = Depends(get_db)):
    youtube_service = YouTubeService()
    state = await youtube_service.get_current_state(session)
    if state is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve system state")
    return {"state": state}
