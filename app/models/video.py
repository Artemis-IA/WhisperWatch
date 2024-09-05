# app/models/video.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.database import Base


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, index=True)
    youtube_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    published_at = Column(DateTime, default=datetime.utcnow)
    transcript = Column(Text)
    video_url = Column(String)
    audio_file = Column(String)
    transcript_file = Column(String)
