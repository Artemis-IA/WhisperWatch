# app/services/scheduler.py
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler
from services.video_hunt import VideoHunterService
from sqlalchemy.ext.asyncio import AsyncSession
from services.youtube_service import YouTubeService
from services.relevance_service import RelevanceDetectionService
from services.download_service import DownloadService
from db.database import get_db
import logging
from prometheus_client import Counter, Gauge, start_http_server
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from fastapi import Depends

# Prometheus Metrics
job_executed_counter = Counter('apscheduler_job_executed_total', 'Total number of jobs executed')
job_error_counter = Counter('apscheduler_job_error_total', 'Total number of job errors')
job_duration_gauge = Gauge('apscheduler_job_duration_seconds', 'Duration of job execution')

# Initialisation des services
youtube_service = YouTubeService()
relevance_service = RelevanceDetectionService()
download_service = DownloadService()
video_hunter = VideoHunterService(
    youtube_service=youtube_service,
    relevance_service=relevance_service,
    download_service=download_service
)

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        logging.basicConfig(level=logging.INFO)
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        start_http_server(8009)  # Expose Prometheus metrics

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logging.info("Scheduler started.")
        else:
            logging.info("Scheduler is already running.")

    def add_job(self, func, trigger, job_id: str, **kwargs):
        """Add or replace a job in the scheduler."""
        self.scheduler.add_job(func, trigger=trigger, id=job_id, **kwargs)
        logging.info(f"Job '{job_id}' added/updated.")

    def remove_job(self, job_id: str):
        """Remove a job from the scheduler."""
        self.scheduler.remove_job(job_id)
        logging.info(f"Job '{job_id}' removed.")

    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logging.info("Scheduler stopped.")

    def job_listener(self, event):
        """Listener for job events to track execution and errors."""
        job_id = event.job_id
        if event.exception:
            logging.error(f"Job {job_id} failed.")
            job_error_counter.inc()  # Increment the error counter
        else:
            logging.info(f"Job {job_id} executed successfully.")
            job_executed_counter.inc()  # Increment the executed jobs counter
            # Capture job duration if available
            if hasattr(event, 'duration'):
                job_duration_gauge.set(event.duration)  # Set duration in seconds

# Exemple de tâche planifiée qui chasse les vidéos
async def scheduled_video_hunt_task():
    async with get_db() as db:  # Generate the db session dynamically
        logging.info(f"Running scheduled video hunt task at {datetime.now()}...")
        keywords = relevance_service.keywords  # Charger les mots-clés du fichier JSON ou de la BDD
        await video_hunter.hunt_videos(db, keywords)

# Démarrage du scheduler
scheduler = Scheduler()

scheduler.add_job(
    scheduled_video_hunt_task,
    trigger=IntervalTrigger(minutes=30),
    job_id='video_hunt_job',
    name='Video hunt and download every 30 minutes',
    replace_existing=True
)

scheduler.start()
