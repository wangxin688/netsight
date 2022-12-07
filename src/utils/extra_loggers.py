""" *******************Important Notice****************************
This extra logger will not be used in web application python file.
It's only used for background executed functions and classes, like cronjobs,
customized tasks executed outside of web application.
Cause filter correlation-id is added for hole lifecycle in api requests.
if code not executed in web application, the log will be ignored forever and
won't be catch by supervisor or docker daemon.
"""
import logging
from logging.config import dictConfig

from src.core.config import settings


def configure_logger():
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "app": {
                "datefmt": "%H:%M:%S",
                "format": "%(levelname)s | %(name)s->%(funcName)s():%(lineno)s - %(message)s",
            }
        },
        "handlers": {
            "app": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "DEBUG",
                "filename": f"{settings.LOG_DIR}/app.log",
                "formatter": "app",
                "when": "W6",
                "encoding": "utf-8",
                "backupCount": "3",
            }
        },
        "loggers": {
            "app": {
                "handlers": ["app"],
                "level": "DEBUG",
            }
        },
    }

    dictConfig(LOGGING)


configure_logger()

logger = logging.getLogger("app")
