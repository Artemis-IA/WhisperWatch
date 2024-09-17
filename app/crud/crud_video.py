# app/crud/crud_video.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.video import Video
from schemas.video import VideoCreate, VideoUpdate
from services.download_service import DownloadService
from services.transcription_service import TranscriptionService
from services.s3_service import S3Service
from services.youtube_service import YouTubeService
import os
import datetime

download_service = DownloadService()
youtube_service = YouTubeService()
transcription_service = TranscriptionService()
s3_service = S3Service()

def make_naive(dt):
    """Convertit un objet datetime offset-aware en offset-naive."""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

# app/crud/crud_video.py
async def create_video(db: AsyncSession, video: VideoCreate):
    # Extract the YouTube ID from the video URL
    youtube_id = youtube_service.extract_video_id(video.video_url)

    # Fetch video details from YouTube
    video_details = youtube_service.get_video_details(video.video_url)
    
    if not video_details:
        raise ValueError("Unable to fetch video details from YouTube.")

    # Extract title, description, and published_at
    title = video_details["title"]
    description = video_details["description"]
    published_at = make_naive(datetime.datetime.fromisoformat(video_details["published_at"].replace("Z", "+00:00")))

    # Proceed with downloading and processing the video
    audio_file = download_service.download_audio(video.video_url)
    if not audio_file:
        raise ValueError("Failed to download the audio.")
    transcript = transcription_service.transcribe_audio(audio_file)

    # Save and upload files
    transcript_file_path = f"{youtube_id}.txt"
    with open(transcript_file_path, "w") as f:
        f.write(transcript)

    audio_url = s3_service.upload_file(audio_file, f'audio/{youtube_id}.mp3')
    transcript_url = s3_service.upload_file(transcript_file_path, f'transcripts/{youtube_id}.txt')

    os.remove(audio_file)
    os.remove(transcript_file_path)

    # Create the Video record in the database
    db_video = Video(
        youtube_id=youtube_id,
        title=title,
        description=description,
        published_at=published_at,
        transcript=transcript,
        video_url=video.video_url,
        audio_file=audio_url,
        transcript_file=transcript_url
    )
    
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)
    return db_video

async def get_videos(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Video).offset(skip).limit(limit))
    return result.scalars().all()

async def get_video(db: AsyncSession, video_id: int):
    result = await db.execute(select(Video).where(Video.id == video_id))
    return result.scalars().first()

async def update_video(db: AsyncSession, video: Video, video_update: VideoUpdate):
    for var, value in vars(video_update).items():
        setattr(video, var, value) if value else None
    await db.commit()
    await db.refresh(video)
    return video

async def delete_video(db: AsyncSession, video_id: int):
    video = await get_video(db, video_id)
    await db.delete(video)
    await db.commit()
    return video
