from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from logging.config import dictConfig

import redis.asyncio as aioreids
import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware

from app.config import settings
from app.consts import Env
from app.exceptions import default_exception_handler, exception_handlers, sentry_ignore_errors
from app.loggers import configure_logger
from app.routers import router
from app.utils import cache
from app.utils.middlewares import RequestMiddleware
from app.utils.openapi import openapi_description


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
        pool = aioreids.ConnectionPool.from_url(
            settings.REDIS_DSN, encoding="utf-8", db=cache.RedisDBType.DEFAULT, decode_response=True
        )
        cache.redis_client = cache.FastapiCache(connection_pool=pool)
        yield
        await pool.disconnect()

    if settings.APP_ENV == Env.PRD.name:  # noqa: SIM300
        sentry_sdk.init(
            dsn=settings.WEB_SENTRY_DSN,
            sample_rate=settings.SENTRY_SAMPLE_RATE,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            release=settings.VERSION,
            send_default_pii=True,
            ignore_errors=sentry_ignore_errors,
        )
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        summary=settings.DESCRIPTION,
        description=openapi_description,
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    app.include_router(router, prefix="/api")
    for handler in exception_handlers:
        app.add_exception_handler(exc_class_or_status_code=handler["exception"], handler=handler["handler"])
    app.add_middleware(RequestMiddleware)
    app.add_middleware(ServerErrorMiddleware, handler=default_exception_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()

if __name__ == "__main__":
    if Env.DEV.name == settings.APP_ENV:
        import uvicorn

        from app.loggers import LOGGING

        uvicorn.run(
            app,
            host="0.0.0.0",  # noqa: S104
            log_config=LOGGING,
            forwarded_allow_ips="*",
            proxy_headers=True,
            loop="uvloop",
            http="httptools",
        )
    else:
        from gunicorn import glogging
        from gunicorn.app.base import BaseApplication

        class GunicornLogger(glogging.Logger):
            def setup(self, cfg: dictConfig) -> None:  # type: ignore  # noqa: PGH003, ARG002
                configure_logger()

        options = {
            "bind": "0.0.0.0:8000",
            "workers": 2,
            "preload": "-",
            "errorlog": "-",
            "accesslog": "-",
            "timeout": 30,
            "forwarded-allow-ip": "*",
        }

        class StandaloneApplication(BaseApplication):
            def __init__(self, app: FastAPI, options: dict) -> None:
                self.options = options
                self.application = app
                super().__init__()

            def load_config(self) -> None:
                if self.cfg:
                    config = {
                        key: value
                        for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None
                    }
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)

            def load(self) -> FastAPI:
                return self.application

        StandaloneApplication(app, options).run()
