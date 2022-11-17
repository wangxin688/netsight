"""ContextVar correlation-id for FastAPI request"""
import types
from contextvars import ContextVar
from typing import Optional

# Middleware
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

# Celery extension
celery_parent_id: ContextVar[Optional[str]] = ContextVar("celery_parent", default=None)
celery_current_id: ContextVar[Optional[str]] = ContextVar(
    "celery_current", default=None
)

# request
request_global = ContextVar("request_global", default=types.SimpleNamespace())


def correlation_id_filter(record):
    """
    Get context correlation_id in FastAPI request
    """
    record["correlation_id"] = correlation_id.get()
    return record["correlation_id"]


def g():
    return request_global.get()
