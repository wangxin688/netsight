# from celery.result import AsyncResult
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from asgi_correlation_id import CorrelationIdMiddleware,correlation_id
from asgi_correlation_id.middleware import is_valid_uuid4
import uuid
import traceback

from src.utils.extensions.async_requests import async_http_req
from src.utils.exceptions import TokenInvalidExpiredError, RefreshTokenInvalidExpiredError, PermissionDenyError, token_invalid_expired_handler, refresh_token_invalid_expired_handler, permission_deny_handler

from tests.loggers import logger

# from fastapi.responses import JSONResponse


router = FastAPI()


@router.get("/tasks/results")
async def get_all_tasks():
    """Get all celery tasks

    Returns:
        _type_: _description_
    """

# router.add_middleware(
#         CorrelationIdMiddleware,
#         header_name="X-Request-ID",
#         generator=lambda: uuid.uuid4().hex,
#         validator=is_valid_uuid4,
#         transformer=lambda a: a,
#     )

async def assert_exception_handler(
    request: Request, exc: AssertionError
) -> JSONResponse:
    # return_info = ERR_NUM_1.dict()
    # return_info.update({"data": jsonable_encoder(str(exc))})
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@router.exception_handler(AssertionError)
async def custom_assert_exception_handler(request, e):
    logger.error(e)
    return await assert_exception_handler(request, e)

import time
from fastapi import Request, Response
@router.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response: Response = await call_next(request)
    except Exception as e:
        logger.error(e)
        logger.info(traceback.print_exc(limit=1))
        response = JSONResponse(status_code=500, content={"detail": str(e)})
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
            "data": response.body.decode("utf-8") if request.path_params.get("audit") else None
        }
        print(data)
        return response

router.add_middleware(
        CorrelationIdMiddleware,
        header_name="X-Request-ID",
        generator=lambda: uuid.uuid4().hex,
        validator=is_valid_uuid4,
        transformer=lambda a: a,
    )



@router.get("/item")
async def get_abc(a, b):
    assert isinstance(a, int), "bad type"
    logger.info(f"receive: {a}, {b}")
    return a + b

@router.get("/test")
async def log_test(a: int, b: int):
    logger.info(f"receive {a} {b}")
    # try:
    res = a / b
    # except ZeroDivisionError as e:
    #     logger.error(e)

    return res


@router.get("/request")
async def req_test(method, url):
    res = await async_http_req(method, url)
    return res
