# app/crud/crud_video.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate
from app.services.download_service import DownloadService
from app.services.transcription_service import TranscriptionService
from app.services.s3_service import S3Service
import os
import datetime

download_service = DownloadService()
transcription_service = TranscriptionService()
s3_service = S3Service()

def make_naive(dt):
    """Convertit un objet datetime offset-aware en offset-naive."""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

async def create_video(db: AsyncSession, video: VideoCreate):
    # Téléchargement de l'audio de la vidéo
    audio_file = download_service.download_audio(video.video_url)

    # Transcription de l'audio
    transcript = transcription_service.transcribe_audio(audio_file)

    # Sauvegarde de la transcription dans un fichier local
    transcript_file_path = f"{video.youtube_id}.txt"
    with open(transcript_file_path, "w") as f:
        f.write(transcript)

    # Téléchargement de l'audio et de la transcription sur MinIO
    audio_url = s3_service.upload_file(audio_file, f'audio/{video.youtube_id}.mp3')
    transcript_url = s3_service.upload_file(transcript_file_path, f'transcripts/{video.youtube_id}.txt')

    # Suppression des fichiers locaux après le téléchargement
    os.remove(audio_file)
    os.remove(transcript_file_path)

    # Création de l'enregistrement vidéo dans la base de données
    db_video = Video(
        youtube_id=video.youtube_id,
        title=video.title,
        description=video.description,
        published_at=make_naive(video.published_at),  # Conversion en offset-naive
        transcript=transcript,
        video_url=video.video_url,
        audio_file=audio_url,
        transcript_file=transcript_url,
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

async def update_video(db: AsyncSession, db_video: Video, video_update: VideoUpdate):
    for var, value in vars(video_update).items():
        setattr(db_video, var, value) if value else None
    await db.commit()
    await db.refresh(db_video)
    return db_video

async def delete_video(db: AsyncSession, video_id: int):
    video = await get_video(db, video_id)
    await db.delete(video)
    await db.commit()
    return video
