# app/api/video_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.celery_app import celery_app
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

@router.post("/start_veille_task", status_code=202)
async def start_veille_task(keywords: str):
    """Lance un job Celery pour surveiller les mots-clés"""
    task = celery_app.send_task('app.tasks.veille_task.perform_veille', args=[keywords])
    return {"task_id": task.id, "status": "started"}

@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """Récupère l'état d'un job Celery"""
    task_result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": task_result.state}