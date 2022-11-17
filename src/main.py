# from celery.result import AsyncResult
import logging
import sys
import time
import traceback
import uuid

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from gunicorn.app.base import BaseApplication
from loguru import logger

from src.core.config import settings
from src.register.context import correlation_id_filter
from src.utils.extensions.async_requests import async_http_req
from src.utils.loggers import (
    JSON_LOGS,
    LOG_LEVEL,
    WORKERS,
    InterceptHandler,
    StubbedGunicornLogger,
)


class StandaloneApplication(BaseApplication):
    """Our Gunicorn application."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"/api/v{settings.MAJAR_VERSION}/openapi.json",
    docs_url=f"/api/v{settings.MAJAR_VERSION}/docs",
    redoc_url=f"/api/v{settings.MAJAR_VERSION}/redocs",
    # exception_handlers=exception_handlers,
)


async def assert_exception_handler(
    request: Request, exc: AssertionError
) -> JSONResponse:
    """assert exception handler for all request"""
    # return_info = ERR_NUM_1.dict()
    # return_info.update({"data": jsonable_encoder(str(exc))})
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(AssertionError)
async def custom_assert_exception_handler(request, e):
    """assert exception handler for all request"""
    logger.error(e)
    return await assert_exception_handler(request, e)


@app.middleware("http")
async def add_audit_handler(request: Request, call_next):
    """add x-request-id, x-process-time and audit log for all request"""
    start_time = time.time()
    try:
        response: Response = await call_next(request)
    except Exception as exc:
        logger.error(exc)
        logger.info(traceback.print_exc(limit=1))
        response = JSONResponse(status_code=500, content={"detail": str(exc)})
    finally:
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        # add glolbal params `audit` to enable or disable rsp data
        data = {
            "duration": process_time,
            "ip": request.client.host,
            "method": request.method,
            "path": request.url.path,
            "parmas": request.path_params,
            "code": response.status_code,
            "x-request-id": correlation_id.get(),
            "data": response.body.decode("utf-8")
            if request.path_params.get("audit")
            else None,
        }
        return response


app.add_middleware(
    CORSMiddleware,
    # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    transformer=lambda a: a,
)


@app.get("/item")
async def get_abc(a, b):
    assert isinstance(a, int), "bad type"
    logger.info(f"receive: {a}, {b}")
    return a + b


@app.get("/test")
async def log_test(a: int, b: int):
    logger.info(f"receive {a} {b}")
    res = a / b
    return res


@app.get("/request")
async def req_test(method, url):
    res = await async_http_req(method, url)
    return res


if __name__ == "__main__":
    intercept_handler = InterceptHandler()
    # logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    # logging.root.handlers = [intercept_handler]
    logging.root.setLevel(LOG_LEVEL)
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <blue>{correlation_id}</blue> | <level>{level: <2}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "serialize": JSON_LOGS,
                "format": fmt,
                "filter": correlation_id_filter,
            }
        ]
    )

    options = {
        "bind": "0.0.0.0",
        "workers": WORKERS,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }

    StandaloneApplication(app, options).run()
