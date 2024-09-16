# app/services/orchestrator.py
import logging
from services.download_service import DownloadService
from services.video_hunt import VideoHunterService
from services.relevance_service import RelevanceDetectionService
from services.youtube_service import YouTubeService
from apscheduler.schedulers.background import BackgroundScheduler

class ServiceOrchestrator:
    def __init__(self):
        logging.info("Initializing services...")
        self.youtube_service = YouTubeService()
        self.relevance_service = RelevanceDetectionService()
        self.video_hunter = VideoHunterService(
            youtube_service=self.youtube_service,
            relevance_service=self.relevance_service
        )
        logging.info("Services initialized.")

    def start_video_hunt(self):
        """Start hunting for videos."""
        keywords = self.relevance_service.keywords
        logging.info(f"Starting video hunt with keywords: {keywords}")
        self.video_hunter.hunt_videos(keywords)

    def schedule_tasks(self):
        """Schedule periodic video hunting tasks."""
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.start_video_hunt,
            trigger='interval',
            minutes=30,  # Adjust the interval as needed
            id='video_hunt_job',
            name='Hunt for relevant videos every 30 minutes',
            replace_existing=True
        )
        scheduler.start()
        logging.info("Scheduled video hunt task.")

    def shutdown_services(self):
        logging.info("Shutting down services...")