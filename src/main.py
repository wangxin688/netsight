import logging
import sys
import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.register.exception_handler import exception_handlers
from src.register.router import router
from src.utils.loggers import (
    JSON_LOGS,
    LOG_LEVEL,
    WORKERS,
    InterceptHandler,
    StandaloneApplication,
    StubbedGunicornLogger,
    correlation_id_filter,
    logger,
)


def create_app():

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redocs"
        # swagger_ui_init_oauth={}
    )
    for handler in exception_handlers:
        app.add_exception_handler(
            exc_class_or_status_code=handler["name"],
            handler=handler["handler"],
        )

    # async def assert_exception_handler(
    #     request: Request, exc: AssertionError
    # ) -> ORJSONResponse:
    #     # return_info = ERR_NUM_1.dict()
    #     # return_info.update({"data": jsonable_encoder(str(exc))})
    #     return ORJSONResponse(status_code=500, content={"detail": str(exc)})

    # @app.exception_handler(AssertionError)
    # async def custom_assert_exception_handler(request, e):
    #     logger.error(e)
    #     return await assert_exception_handler(request, e)

    app.add_middleware(
        CorrelationIdMiddleware,
        header_name="X-Request-ID",
        generator=lambda: uuid.uuid4().hex,
        validator=is_valid_uuid4,
        transformer=lambda a: a,
    )

    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")

    return app


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
        "bind": "0.0.0.0:8000",
        "workers": WORKERS,
        "timeout": 30,
        "max-requests": 200,
        "max-requests-jitter": 20,
        "preload": "-",
        "forwarded-allow-ips": "*",
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }
    app = create_app()
    try:
        StandaloneApplication(app, options).run()
    except Exception as e:
        print(e)
