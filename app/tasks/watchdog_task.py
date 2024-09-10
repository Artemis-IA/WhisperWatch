
# app/tasks/watchdog_task.py
# app/tasks/watchdog_task.py
import json
from celery import shared_task
from app.db.database import get_db
from app.crud.crud_video import get_video, create_video, VideoCreate
from app.services.youtube_service import YouTubeService
from app.services.download_service import DownloadService
from app.services.transcription_service import TranscriptionService
from app.services.s3_service import S3Service
import logging
import os

# Define the path to the keywords JSON file
KEYWORDS_FILE_PATH = "app/keywords.json"

def load_keywords():
    """Loads search keywords from a JSON configuration file."""
    with open(KEYWORDS_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data['queries']

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
async def perform_veille(self):
    """Periodic task to search for new YouTube videos using dynamic keywords."""
    async with get_db() as session:
        youtube_service = YouTubeService()
        download_service = DownloadService()
        transcription_service = TranscriptionService()
        s3_service = S3Service()

        # Load queries dynamically from the configuration file
        queries = load_keywords()

        try:
            for query in queries:
                videos = youtube_service.search_videos(query)
                for item in videos:
                    video_id = item['id']['videoId']
                    existing = await get_video(session, video_id)
                    if not existing:
                        title = item['snippet']['title']
                        description = item['snippet']['description']
                        published_at = item['snippet']['publishedAt']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"

                        # Download the audio
                        audio_file = download_service.download_audio(video_url)

                        # Transcribe the audio
                        transcript = transcription_service.transcribe_audio(audio_file)

                        # Save the video in the database
                        new_video = await create_video(session, VideoCreate(
                            youtube_id=video_id,
                            title=title,
                            description=description,
                            published_at=published_at,
                            transcript=transcript,
                            video_url=video_url,
                        ))

                        # Upload the audio file to S3
                        s3_key = f"audios/{video_id}.mp3"
                        audio_s3_url = s3_service.upload_file(audio_file, s3_key)
                        new_video.audio_file = audio_s3_url
                        await session.commit()
        except Exception as e:
            logging.error(f"Failed to process videos: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
