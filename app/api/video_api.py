# app/api/video_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.video import VideoCreate, VideoOut, VideoUpdate
from app.crud.crud_video import get_videos, get_video, create_video, update_video, delete_video

router = APIRouter()

@router.get("/", response_model=list[VideoOut])
async def read_videos(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    videos = await get_videos(db, skip=skip, limit=limit)
    return videos

@router.get("/{video_id}", response_model=VideoOut)
async def read_video(video_id: int, db: AsyncSession = Depends(get_db)):
    video = await get_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.post("/", response_model=VideoOut)
async def create_new_video(video: VideoCreate, db: AsyncSession = Depends(get_db)):
    return await create_video(db, video)

@router.put("/{video_id}", response_model=VideoOut)
async def update_existing_video(video_id: int, video_update: VideoUpdate, db: AsyncSession = Depends(get_db)):
    video = await get_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return await update_video(db, video, video_update)

@router.delete("/{video_id}", response_model=VideoOut)
async def delete_existing_video(video_id: int, db: AsyncSession = Depends(get_db)):
    video = await get_video(db, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return await delete_video(db, video_id)
