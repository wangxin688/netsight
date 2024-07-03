from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as aioreids
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware

from src.core.config import _Env, settings
from src.core.errors.exceptions import default_exception_handler, exception_handlers, sentry_ignore_errors
from src.libs.redis import cache
from src.register.middlewares import RequestMiddleware
from src.register.openapi import get_open_api_intro, get_stoplight_elements_html
from src.register.routers import router


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
        pool = aioreids.ConnectionPool.from_url(
            settings.REDIS_DSN, encoding="utf-8", db=cache.RedisDBType.DEFAULT, decode_response=True
        )
        cache.redis_client = cache.FastapiCache(connection_pool=pool)
        yield
        await pool.disconnect()

    if _Env.PROD.name == settings.ENV:
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
        description=get_open_api_intro(),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    @app.get(
        "/api/health", include_in_schema=False, tags=["Internal"], operation_id="e7372032-61c5-4e3d-b2f1-b788fe1c52ba"
    )
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/api/version", include_in_schema=False, tags=["Internal"], operation_id="47918987-15d9-4eea-8c29-e73cb009a4d5"
    )
    def version() -> dict[str, str]:
        return {"version": settings.VERSION}

    @app.get(
        "/api/elements", include_in_schema=False, tags=["Docs"], operation_id="1a4987dd-6c38-4502-a879-3fe35050ae38"
    )
    def get_stoplight_elements() -> HTMLResponse:
        return get_stoplight_elements_html(openapi_url="/api/openapi.json", title=settings.PROJECT_NAME)

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
