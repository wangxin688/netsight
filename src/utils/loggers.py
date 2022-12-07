import logging
import sys

from asgi_correlation_id.context import correlation_id
from gunicorn.glogging import Logger
from loguru import logger

from src.core.config import settings

LOG_LEVEL = settings.LOG_LEVEL
JSON_LOGS = settings.JSON_LOGS
WORKERS = settings.WORKERS


def correlation_id_filter(record):
    record["correlation_id"] = correlation_id.get()
    return record["correlation_id"]


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class GunicornLogger(Logger):
    def setup(self, cfg) -> None:
        handler = InterceptHandler()
        fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
        fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <blue>{correlation_id}</blue> | <level>{level: <2}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        # Add log handler to logger and set log level
        self.error_log.addHandler(handler)
        self.error_log.setLevel(settings.LOG_LEVEL)
        self.access_log.addHandler(handler)
        self.access_log.setLevel(settings.LOG_LEVEL)

        # Configure logger before gunicorn starts logging
        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "level": settings.LOG_LEVEL,
                    "format": fmt,
                    "filter": correlation_id_filter,
                }
            ]
        )


def configure_logger() -> None:
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_LEVEL)

    # Remove all log handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Configure logger (again) if gunicorn is not used
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <blue>{correlation_id}</blue> | <level>{level: <2}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": settings.LOG_LEVEL,
                "format": fmt,
                "filter": correlation_id_filter,
            }
        ]
    )
