# app/services/video_hunt.py

import logging
from crud.crud_video import create_video
from schemas.video import VideoCreate
from prometheus_client import Counter

# Prometheus Counters
video_hunt_counter = Counter('video_hunt_executed_total', 'Total number of videos hunted')
relevant_video_counter = Counter('relevant_video_found_total', 'Total number of relevant videos found')

class VideoHunterService:
    def __init__(self, youtube_service, relevance_service, download_service):
        self.youtube_service = youtube_service
        self.relevance_service = relevance_service
        self.download_service = download_service

    async def hunt_videos(self, db, keywords, max_results=50):
        """Hunt for videos based on keywords and download relevant ones."""
        video_hunt_counter.inc()  # Increment Prometheus counter for each hunt
        for keyword in keywords:
            videos = self.youtube_service.search_videos(query=keyword, max_results=max_results)
            for video in videos:
                metadata = {
                    "title": video["snippet"]["title"],
                    "description": video["snippet"]["description"],
                }
                # Combine title and description into a single string for relevance checking
                content = f"{metadata['title']} {metadata['description']}"

                # Check relevance using the RelevanceDetectionService
                if self.relevance_service.is_relevant(content):
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    logging.info(f"Relevant video found: {metadata['title']}")
                    relevant_video_counter.inc()  # Increment Prometheus counter for relevant videos

                    # Download audio and get URL from S3/MinIO
                    audio_url = self.download_service.download_audio(video_url)

                    if audio_url:
                        # Create VideoCreate object
                        video_create = VideoCreate(
                            video_url=video_url,
                            title=metadata['title'],
                            description=metadata['description'],
                            audio_file=audio_url
                        )

                        # Use CRUD method to create video entry in PostgreSQL
                        try:
                            await create_video(db, video_create)
                            logging.info(f"Video successfully created in the database: {metadata['title']}")
                        except Exception as e:
                            logging.error(f"Error creating video in the database: {e}")
