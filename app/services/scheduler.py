# app/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from prometheus_client import Counter, Gauge, start_http_server
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

# Prometheus Metrics
job_executed_counter = Counter('apscheduler_job_executed_total', 'Total number of jobs executed')
job_error_counter = Counter('apscheduler_job_error_total', 'Total number of job errors')
job_duration_gauge = Gauge('apscheduler_job_duration_seconds', 'Duration of job execution')

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        logging.basicConfig(level=logging.INFO)
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # Expose Prometheus metrics endpoint
        start_http_server(8009)

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


# Global scheduler instance
scheduler = Scheduler()

# Example scheduled task (modify as needed)
def scheduled_download_task():
    logging.info(f"Running scheduled download task at {datetime.now()}...")

# Adding an initial job for demonstration purposes
scheduler.add_job(
    scheduled_download_task,
    IntervalTrigger(minutes=10),
    job_id='video_hunt_job',
    name='Video hunt and download every 10 minutes',
    replace_existing=True
)
scheduler.start()

