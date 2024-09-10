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
    
    def extract_video_id(self, youtube_url):
        """Extract video ID from a YouTube URL."""
        return youtube_url.split("v=")[1]

    def get_video_details(self, youtube_url):
        """Fetch details like title, description, published date for a video."""
        video_id = self.extract_video_id(youtube_url)
        request = self.youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        )
        response = request.execute()

        if response["items"]:
            video_info = response["items"][0]["snippet"]
            return {
                "title": video_info["title"],
                "description": video_info["description"],
                "published_at": video_info["publishedAt"]
            }
        return None