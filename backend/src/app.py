from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as aioreids
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware

from src.core.config import _Env, settings
from src.core.database.session import async_engine
from src.core.errors.exception_handlers import default_exception_handler, exception_handlers, sentry_ignore_errors
from src.features.admin.views import AdminAuth
from src.libs.redis import session
from src.register.middlewares import RequestMiddleware
from src.register.openapi import get_open_api_intro, get_stoplight_elements_html
from src.register.routers import router


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


def add_views(admin: Admin) -> None:
    # remove the default admin views if I have time in future to build frontend by React
    # it's only and POC for now and simplified for the demo to admin user.
    # all views should be added to views.py without any migical implementation
    from src.features.admin.views import GroupView, RoleView, UserView
    from src.features.circuit.views import CircuitView
    from src.features.dcim.views import DeviceView
    from src.features.intend.views import (
        CircuitTypeView,
        DeviceRoleView,
        DeviceTypeView,
        IPRoleView,
        ManufacturerView,
        PlatformView,
    )
    from src.features.ipam.views import BlockView, PrefixView, VLANView
    from src.features.netconfig.views import (
        AuthCredentialView,
        BaseLineConfigView,
        JinjaTemplateView,
        TextFsmTemplateView,
    )
    from src.features.org.views import LocationView, SiteGroupView, SiteView

    admin.add_view(DeviceTypeView)
    admin.add_view(PlatformView)
    admin.add_view(ManufacturerView)
    admin.add_view(IPRoleView)
    admin.add_view(CircuitTypeView)
    admin.add_view(DeviceRoleView)
    admin.add_view(BaseLineConfigView)
    admin.add_view(AuthCredentialView)
    admin.add_view(JinjaTemplateView)
    admin.add_view(TextFsmTemplateView)
    admin.add_view(SiteGroupView)
    admin.add_view(SiteView)
    admin.add_view(LocationView)
    admin.add_view(DeviceView)
    admin.add_view(BlockView)
    admin.add_view(PrefixView)
    admin.add_view(VLANView)
    admin.add_view(CircuitView)
    admin.add_view(GroupView)
    admin.add_view(RoleView)
    admin.add_view(UserView)


auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
app = create_app()
admin = Admin(
    app=app, engine=async_engine, authentication_backend=auth_backend, title=settings.PROJECT_NAME, debug=True
)
add_views(admin)
