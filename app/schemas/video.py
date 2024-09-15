# app/schemas/video.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoBase(BaseModel):
    video_url: str  # Seul ce champ est fourni par l'utilisateur

class VideoCreate(VideoBase):
    pass  # No youtube_id, it will be handled by the backend

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    transcript: Optional[str] = None

class VideoOut(VideoBase):
    id: int
    youtube_id: str
    title: str
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    transcript: Optional[str] = None
    audio_file: Optional[str] = None
    transcript_file: Optional[str] = None

    class Config:
        from_attributes = True
