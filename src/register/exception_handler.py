import sys
import traceback

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.utils.error_code import (
    ERR_NUM_1,
    ERR_NUM_500,
    ERR_NUM_4001,
    ERR_NUM_4002,
    ERR_NUM_4003,
    ERR_NUM_4004,
    ERR_NUM_4011,
)
from src.utils.exceptions import (
    PermissionDenyError,
    ResourceNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TokenInvalidForRefreshError,
    TokenNotProvidedError,
)
from src.utils.loggers import logger


async def token_not_provided_handler(
    request: Request, exc: TokenNotProvidedError
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4001.dict())


async def token_invalid_handler(
    request: Request, exc: TokenInvalidError
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4001.dict())


async def invalid_token_for_refresh_handler(
    request: Request, exc: TokenInvalidForRefreshError
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4011.dict())


async def token_expired_handler(
    request: Request, exc: TokenExpiredError
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4002.dict())


async def permission_deny_handler(
    request: Request, exc: PermissionDenyError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ERR_NUM_4003.dict(),
    )


async def resource_not_found_handler(
    request: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4004.dict())


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error("Request validation error", exc)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "data": jsonable_encoder(exc.errors()),
            "msg": "validation error, please check input",
        },
    )


async def assert_exception_handler(
    request: Request, exc: AssertionError
) -> JSONResponse:
    return_info = ERR_NUM_1.dict()
    return_info.update({"data": jsonable_encoder(str(exc))})
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_info)


async def base_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    ex_type, _, ex_traceback = sys.exc_info()
    trace_back = traceback.format_list(traceback.extract_tb(ex_traceback)[-1:])[-1]

    logger.error("Exception type : %s " % ex_type.__name__)
    logger.error("Stack trace : %s" % trace_back)
    return_info = ERR_NUM_500
    return_info.data = jsonable_encoder(str(exc))


exception_handlers = [
    {
        "name": TokenNotProvidedError,
        "handler": token_not_provided_handler,
    },
    {
        "name": TokenInvalidError,
        "handler": token_invalid_handler,
    },
    {
        "name": TokenInvalidForRefreshError,
        "handler": invalid_token_for_refresh_handler,
    },
    {
        "name": TokenExpiredError,
        "handler": token_expired_handler,
    },
    {
        "name": PermissionDenyError,
        "handler": permission_deny_handler,
    },
    {
        "name": ResourceNotFoundError,
        "handler": resource_not_found_handler,
    },
    {
        "name": RequestValidationError,
        "handler": request_validation_exception_handler,
    },
    {
        "name": AssertionError,
        "handler": assert_exception_handler,
    },
    {
        "name": Exception,
        "handler": base_exception_handler,
    },
]
