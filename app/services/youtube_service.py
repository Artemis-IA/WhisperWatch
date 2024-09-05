# app/services/youtube_service.py
from googleapiclient.discovery import build
from app.core.config import settings

class YouTubeService:
    def __init__(self):
        self.youtube = build(
            "youtube", "v3",
            developerKey=settings.YOUTUBE_API_KEY
        )

    def search_videos(self, query, max_results=10):
        request = self.youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            order="date"
        )
        response = request.execute()
        return response.get("items", [])
