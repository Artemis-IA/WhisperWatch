# app/api/relevance_detection_api.py
from fastapi import APIRouter, HTTPException
from services.relevance_service import RelevanceDetectionService
from services.youtube_service import YouTubeService

router = APIRouter()

@router.post("/check_relevance/")
async def check_relevance(video_url: str):
    try:
        # Fetch video details from YouTube
        youtube_service = YouTubeService()
        video_metadata = youtube_service.get_video_details(video_url)

        if not video_metadata:
            raise HTTPException(status_code=404, detail="Video not found or invalid URL")

        # Combine title and description into a single string
        content = f"{video_metadata['title']} {video_metadata['description']}"

        # Check relevance using RelevanceDetectionService
        relevance_service = RelevanceDetectionService()
        is_relevant = relevance_service.is_relevant(content)

        return {"video_url": video_url, "is_relevant": is_relevant}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking video relevance: {str(e)}")
