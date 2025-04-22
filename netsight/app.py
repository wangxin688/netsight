from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as aioreids
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware

from netsight.core.config import _Env, settings
from netsight.core.errors.exception_handlers import default_exception_handler, exception_handlers, sentry_ignore_errors
from netsight.libs.redis import session
from netsight.register.middlewares import RequestMiddleware
from netsight.register.openapi import get_open_api_intro, get_stoplight_elements_html
from netsight.register.routers import router


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
        pool = aioreids.ConnectionPool.from_url(
            settings.REDIS_DSN, encoding="utf-8", db=session.RedisDBType.DEFAULT, decode_response=True
        )
        session.redis_client = session.FastapiCache(connection_pool=pool)
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
        "/api/elements", tags=["Docs"], include_in_schema=False, operation_id="1a4987dd-6c38-4502-a879-3fe35050ae38"
    )
    def get_stoplight_elements() -> HTMLResponse:
        return get_stoplight_elements_html(
            openapi_url="/api/openapi.json", title=settings.PROJECT_NAME, base_path="/api/elements"
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
