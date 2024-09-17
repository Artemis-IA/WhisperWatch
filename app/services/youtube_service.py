# app/services/youtube_service.py
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from core.config import settings

class YouTubeService:
    def __init__(self):
        self.youtube = build(
            "youtube", "v3",
            developerKey=settings.YOUTUBE_API_KEY
        )

    def extract_video_id(self, youtube_url):
        """Extract video ID from a YouTube URL."""
        if 'v=' in youtube_url:
            return youtube_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in youtube_url:
            return youtube_url.split('youtu.be/')[1].split('?')[0]
        else:
            raise ValueError("Invalid YouTube URL")

    def get_video_details(self, youtube_url):
        """Fetch details like title, description, and published date for a video."""
        video_id = self.extract_video_id(youtube_url)

        try:
            request = self.youtube.videos().list(
                part="snippet",
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
            else:
                raise ValueError("Video not found on YouTube.")
        except Exception as e:
            print(f"Failed to fetch video details: {e}")
            return None


    def search_videos(self, query, max_results=10, days_ago=30):
        """Search for recent videos based on a query and filter by date."""
        # Filtrer les vidéos postées dans les 30 derniers jours
        published_after = (datetime.now() - timedelta(days=days_ago)).isoformat("T") + "Z"
        
        request = self.youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            order="date",  # Trier par date ou par pertinence (relevance)
            publishedAfter=published_after
        )
        
        response = request.execute()
        return response.get("items", [])