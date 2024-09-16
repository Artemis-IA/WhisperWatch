# app/services/video_hunt.py

import numpy as np
from services.youtube_service import YouTubeService
from services.relevance_service import RelevanceDetectionService
from services.download_service import DownloadService
import logging

class VideoHunterService:
    def __init__(self, youtube_service, relevance_service):
        self.youtube_service = youtube_service
        self.relevance_service = relevance_service
        self.download_service = DownloadService()

    def hunt_videos(self, keywords, max_results=50):
        """Hunt for videos based on keywords and download relevant ones."""
        for keyword in keywords:
            videos = self.youtube_service.search_videos(query=keyword, max_results=max_results)
            for video in videos:
                metadata = {
                    "title": video["snippet"]["title"],
                    "description": video["snippet"]["description"],
                }

                # Check relevance using the RelevanceDetectionService
                if self.relevance_service.is_relevant(metadata):
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    logging.info(f"Relevant video found: {metadata['title']}")
                    # Schedule the video for download
                    self.download_service.consume_and_download(video_url)

