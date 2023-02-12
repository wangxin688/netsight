# -*- encoding: utf-8 -*-
"""
@Time    :   2023/02/11 16:04:00
@Author  :   jeffry 
@Version :   1.0
@Contact :   wangxin.jeffry@gmail.com
@Description :
"""


import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.app.auth.services import permission_dict_generate
from src.core.config import settings
from src.register.exception_handler import exception_handlers
from src.register.router import router
from src.utils.loggers import configure_logger


def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        swagger_ui_init_oauth={},
        contact={
            "name": "JeffryWang",
            "email": "wangxin.jeffry@gmail.com",
            "url": "https://github.com/wangxin688",
        },
        license={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    )
    for handler in exception_handlers:
        app.add_exception_handler(
            exc_class_or_status_code=handler["name"],
            handler=handler["handler"],
        )

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

    @app.on_event("startup")
    async def startup_event():
        logger.info("execute on startup event ")
        permissions = await permission_dict_generate()
        app.state.permissions = permissions
        configure_logger()
        logger.info("execute on startup event done")

    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    # gunicorn version
    # options = {
    #     "bind": "0.0.0.0:8000",
    #     "workers": 8,
    #     "timeout": 30,
    #     "max-requests": 200,
    #     "max-requests-jitter": 20,
    #     "preload": "-",
    #     "forwarded-allow-ips": "*",
    #     "accesslog": "-",
    #     "errorlog": "-",
    #     "worker_class": "uvicorn.workers.UvicornWorker",
    #     "logger_class": GunicornLogger,
    # }

    # try:
    #     StandaloneApplication(app, options).run()
    # except Exception:
    #     print(traceback.format_exc())

    # uvicorn version

    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
