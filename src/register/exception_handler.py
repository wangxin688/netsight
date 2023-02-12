import sys
import traceback

from asgi_correlation_id import correlation_id
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError

from src.app.deps import get_locale
from src.utils.error_code import (
    ERR_NUM_401,
    ERR_NUM_402,
    ERR_NUM_403,
    ERR_NUM_404,
    ERR_NUM_411,
    ERR_NUM_422,
    ERR_NUM_500,
    ResponseMsg
)
from src.utils.exceptions import (
    PermissionDenyError,
    ResourceNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TokenInvalidForRefreshError,
    TokenNotProvidedError
)
from src.utils.i18n_loaders import _


async def token_not_provided_handler(request: Request, exc: TokenNotProvidedError) -> JSONResponse:
    logger.error("Token not provided")
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_401.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_401.message, locale=locale),
        ).dict(),
    )


async def token_invalid_handler(request: Request, exc: TokenInvalidError) -> JSONResponse:
    logger.error("Token invalid")
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_401.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_401.message, locale=locale),
        ).dict(),
    )


async def invalid_token_for_refresh_handler(request: Request, exc: TokenInvalidForRefreshError) -> JSONResponse:
    logger.error("Token invalid for refresh")
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_411.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_411.message, locale=locale),
        ).dict(),
    )


async def token_expired_handler(request: Request, exc: TokenExpiredError) -> JSONResponse:
    logger.error("Token expired")
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_402.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_402.message, locale=locale),
        ).dict(),
    )


async def permission_deny_handler(request: Request, exc: PermissionDenyError) -> JSONResponse:
    logger.error("Permission Deny")
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_403.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_403.message, locale=locale),
        ).dict(),
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    logger.error("Resource not found")
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_404.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_404.message, locale=locale),
        ).dict(),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error("Request validation error", exc)
    ex_type, _tmp, ex_traceback = sys.exc_info()
    trace_back = traceback.format_list(traceback.extract_tb(ex_traceback)[-1:])[-1]
    logger.error("Exception type : %s " % ex_type.__name__)
    logger.error("Stack trace : %s" % trace_back)
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_422.code,
            data=jsonable_encoder(str(exc)),
            locale=locale,
            message=_(ERR_NUM_422.message, locale=locale),
        ).dict(),
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.error("Data validation error with pydantic", exc)
    ex_type, _tmp, ex_traceback = sys.exc_info()
    trace_back = traceback.format_list(traceback.extract_tb(ex_traceback)[-1:])[-1]

    logger.error("Exception type : %s " % ex_type.__name__)
    logger.error("Stack trace : %s" % trace_back)

    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_422.code,
            data=jsonable_encoder(str(exc)),
            locale=locale,
            message=_(ERR_NUM_422.message, locale=locale),
        ).dict(),
    )


async def assert_exception_handler(request: Request, exc: AssertionError) -> JSONResponse:
    locale = get_locale(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_422.code,
            data=jsonable_encoder(str(exc)),
            locale=locale,
            message=_(ERR_NUM_422.message, locale=locale),
        ).dict(),
    )


async def base_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    ex_type, _tmp, ex_traceback = sys.exc_info()
    trace_back = traceback.format_list(traceback.extract_tb(ex_traceback)[-1:])[-1]
    logger.error("Exception type : %s " % ex_type.__name__)
    logger.error("Stack trace : %s" % trace_back)
    locale = get_locale(request)
    request_id = correlation_id.get()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseMsg(
            code=ERR_NUM_500.code,
            data=jsonable_encoder(str(exc)),
            locale=locale,
            message=_(ERR_NUM_500.message, locale=locale, request_id=request_id),
        ).dict(),
    )


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
        "name": ValidationError,
        "handler": validation_exception_handler,
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
