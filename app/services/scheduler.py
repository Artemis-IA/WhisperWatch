# app/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        logging.basicConfig(level=logging.INFO)

    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logging.info("Scheduler started.")

    def add_job(self, func, trigger, **kwargs):
        """Add a job to the scheduler."""
        self.scheduler.add_job(func, trigger=trigger, **kwargs)

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()

# Global scheduler instance
scheduler = Scheduler()

# Schedule a video download every 10 minutes (you can adjust the interval)
def scheduled_download_task():
    logging.info(f"Running scheduled download task at {datetime.now()}...")
    # Call video hunt and download logic here
    # e.g., orchestrator.start_video_hunt()

scheduler.add_job(
    scheduled_download_task, 
    IntervalTrigger(minutes=10), 
    id='video_hunt_job', 
    name='Video hunt and download every 10 minutes', 
    replace_existing=True
)
scheduler.start()
