# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_BACKEND = os.getenv("CELERY_BACKEND")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

settings = Settings()
