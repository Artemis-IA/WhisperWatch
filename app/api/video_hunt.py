# app/api/video_hunt_api.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.video_hunt import VideoHunterService
from db.database import get_db

router = APIRouter()

@router.get("/hunt_videos/", response_model=list)
async def hunt_videos(db: AsyncSession = Depends(get_db)):
    try:
        # Initialize the VideoHunterService
        video_hunter_service = VideoHunterService(
            youtube_service=youtube_service,
            keyword_manager=keyword_manager,
            relevance_service=relevance_service,
            etdqn=etdqn
        )

        relevant_videos = video_hunter_service.hunt_videos()
        return relevant_videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during video hunting: {str(e)}")
