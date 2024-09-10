# app/core/celery_app.py
from celery import Celery
from app.core.config import settings
from celery.schedules import crontab
from prometheus_client import Counter
from celery.signals import task_prerun



celery_app = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND
)

# Celery Beat schedule
celery_app.conf.update(
    beat_schedule={
        'perform-veille-hourly': {
            'task': 'app.tasks.watchdog_task.perform_veille',
            'schedule': crontab(minute=0, hour='*/1'),
        },
    },
    timezone='UTC',
)

# Prometheus Counter for Celery tasks
celery_task_counter = Counter('celery_tasks_total', 'Total number of Celery tasks executed', ['task_name'])

# Signal handler to increment Prometheus counter before a task starts
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, *args, **kwargs):
    """Increment the Prometheus counter every time a Celery task starts."""
    celery_task_counter.labels(task_name=task.name).inc()