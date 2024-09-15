# app/api/video_hunt_api.py
from fastapi import APIRouter
from services.video_hunt import VideoHunterService

router = APIRouter()

@router.post("/video-hunt", response_model=dict)
async def hunt_videos():
    hunter_service = VideoHunterService()
    relevant_videos = hunter_service.hunt_videos()
    return {"status": "success", "relevant_videos": relevant_videos}
