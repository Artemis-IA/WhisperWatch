from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema for video
class VideoBase(BaseModel):
    youtube_id: str
    title: str
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    transcript: Optional[str] = None
    video_url: str

# Schema for creating a video
class VideoCreate(VideoBase):
    pass

# Schema for updating a video
class VideoUpdate(VideoBase):
    pass

# Schema for returning video data
class VideoOut(VideoBase):
    id: int

    class Config:
        from_attributes = True
