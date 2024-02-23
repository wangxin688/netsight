import logging
from logging import LogRecord, setLogRecordFactory
from logging.config import dictConfig

from app._types import P
from app.utils.context import request_id_ctx


class LogExtraFactory(LogRecord):
    def __init__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__(*args, **kwargs)
        request_id = request_id_ctx.get() or "N/A"
        self.__dict__["request_id"] = request_id


LOGGING = {
    "version": 1,
    "disable_existing_loggers": 0,
    "formatters": {
        "default": {
            "format": (
                "%(levelname)s | %(asctime)s | %(request_id)s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
            ),
        },
        "celery": {
            "format": (
                "%(levelname)s | %(asctime)s | %(request_id)s [%(celery_parent_id)s-%(celery_current_id)s] |"
                " %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
            ),
        },
    },
    "handlers": {
        "stdout": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
        "celery": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "celery",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "gunicorn.access": {"handlers": ["stdout"], "propagate": True, "level": "INFO"},
        "gunicorn.error": {"handlers": ["stdout"], "propagate": True, "level": "INFO"},
        "celery": {"handlers": ["stdout"], "propagate": False, "level": "INFO"},
        "celery.app.trace": {"handlers": ["stdout"], "propagate": False, "level": "INFO"},
        "": {"handlers": ["stdout"], "propagate": True, "level": "INFO"},
    },
}


def configure_logger(config: dict | None = None) -> None:
    if config is None:
        config = LOGGING
    dictConfig(config)
    setLogRecordFactory(LogExtraFactory)
    requests_log = logging.getLogger("httpx")
    requests_log.addHandler(logging.NullHandler())
    requests_log.propagate = False


configure_logger()
