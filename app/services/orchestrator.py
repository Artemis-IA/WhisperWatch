# app/services/orchestrator.py
import logging
import asyncio
from services.download_service import DownloadService
from services.video_hunt import VideoHunterService
from services.relevance_service import RelevanceDetectionService
from services.youtube_service import YouTubeService
from apscheduler.schedulers.background import BackgroundScheduler
from db.database import get_db

class ServiceOrchestrator:
    def __init__(self):
        logging.info("Initializing services...")
        self.youtube_service = YouTubeService()
        self.relevance_service = RelevanceDetectionService()
        self.download_service = DownloadService()
        self.video_hunter = VideoHunterService(
            youtube_service=self.youtube_service,
            relevance_service=self.relevance_service,
            download_service=self.download_service
        )
        self.lock = asyncio.Lock()

    async def start_video_hunt(self):
        """Start hunting for videos."""
        keywords = self.relevance_service.keywords
        logging.info(f"Starting video hunt with keywords: {keywords}")

        # Obtenir une session de base de données
        async with get_db() as db:
            await self.video_hunter.hunt_videos(db, keywords)

    def schedule_tasks(self, minutes_interval=5):
        """Schedule periodic video hunting tasks."""
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.start_video_hunt_wrapper,  # Appeler le wrapper ici
            trigger='interval',
            minutes=minutes_interval,
            id='video_hunt_job',
            name=f'Hunt for relevant videos every {minutes_interval} minutes',
            replace_existing=True
        )
        scheduler.start()

        logging.info("Scheduled video hunt task.")

    def shutdown_services(self):
        logging.info("Shutting down services...")

    def start_video_hunt_wrapper(self):
        """Wrapper pour appeler la tâche async dans un job APScheduler"""
        import asyncio
        asyncio.run(self.start_video_hunt())
