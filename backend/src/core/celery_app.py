import logging
from collections.abc import Callable, Coroutine
from logging.config import dictConfig
from typing import Any, TypeVar

from anyio.from_thread import start_blocking_portal
from celery import Celery
from celery.signals import setup_logging

from src.core.config import settings
from src.core.utils.loggers import LOGGING

_R = TypeVar("_R")

celery_app = Celery(
    __name__,
    backend=settings.CELERY_BACKEND_URL,
    broker=settings.CELERY_BROKER_URL,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    result_persistence=True,
    imports=(),
)


def async_task(func: Callable[..., Coroutine[Any, Any, _R]]) -> _R:
    def wrapper(*args: Any) -> _R:
        with start_blocking_portal() as portal:
            return portal.call(func, *args)

    return wrapper  # type: ignore  # noqa: PGH003


@setup_logging.connect
def _setup_logging(**kwargs: Any) -> None:  # noqa: ARG001
    dictConfig(LOGGING)
    logging.getLogger("child").propagate = False
