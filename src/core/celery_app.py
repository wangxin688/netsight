from celery import Celery

from src.core.config import settings


class Config:
    broker = settings.BROKER_URL
    backend = settings.RESULT_BACKEND
    task_acks_late = True
    task_reject_on_worker_lost = True
    worker_max_tasks_per_child = 2
    task_track_started = True
    imports = ("src.api.auth.tasks", "src.api.dcim.tasks")


celery_app = Celery(__name__)

celery_app.config_from_object(Config)
