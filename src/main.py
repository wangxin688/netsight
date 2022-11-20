import time
import traceback
import uuid

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api.auth.views import auth_router
from tests.loggers import logger

app = FastAPI()


async def assert_exception_handler(
    request: Request, exc: AssertionError
) -> ORJSONResponse:
    # return_info = ERR_NUM_1.dict()
    # return_info.update({"data": jsonable_encoder(str(exc))})
    return ORJSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(AssertionError)
async def custom_assert_exception_handler(request, e):
    logger.error(e)
    return await assert_exception_handler(request, e)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response: Response = await call_next(request)
    except Exception as e:
        logger.error(e)
        logger.info(traceback.print_exc())
        response = ORJSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        # add glolbal params `audit` to enable or disable rsp data
        data = {
            "x-process-time": process_time,
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
        logger.info(data)
        return response


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

app.include_router(auth_router, prefix="/auth", tags=["auth"])
