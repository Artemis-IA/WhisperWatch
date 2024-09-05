# app/core/celery_app.py
from celery import Celery
from app.core.config import settings
from celery.schedules import crontab


celery_app = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND
)

celery_app.conf.update(
    beat_schedule={
        'perform-veille-hourly': {
            'task': 'app.tasks.veille_task.perform_veille',
            'schedule': crontab(minute=0, hour='*/1'),
        },
    },
    timezone='UTC',
)
