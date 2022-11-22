from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from src.utils.error_code import (
    ERR_NUM_1,
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
) -> ORJSONResponse:
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4001.dict())


async def token_invalid_handler(
    request: Request, exc: TokenInvalidError
) -> ORJSONResponse:
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4001.dict())


async def invalid_token_for_refresh_handler(
    request: Request, exc: TokenInvalidForRefreshError
) -> ORJSONResponse:
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4011.dict())


async def token_expired_handler(
    request: Request, exc: TokenExpiredError
) -> ORJSONResponse:
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=ERR_NUM_4002.dict())


async def permission_deny_handler(
    request: Request, exc: PermissionDenyError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content=ERR_NUM_4003._asdict(),
    )


async def resource_not_found_handler(
    request: Request, exc: ResourceNotFoundError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_200_OK, content=ERR_NUM_4004._asdict()
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    logger.error("Request validation error", exc)
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "data": jsonable_encoder(exc.errors()),
            "msg": "validation error, please check input",
        },
    )


async def assert_exception_handler(
    request: Request, exc: AssertionError
) -> ORJSONResponse:
    return_info = ERR_NUM_1.dict()
    return_info.update({"data": jsonable_encoder(str(exc))})
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=return_info)


# exception_handlers = {
#     "token_not_provided_handler": token_not_provided_handler,
#     "token_invalid_handler": token_invalid_handler,
#     "invalid_token_for_refresh_handler": invalid_token_for_refresh_handler,
#     "token_expired_handler": token_invalid_handler,
#     "permission_deny_handler": permission_deny_handler,
#     "resource_not_found_handler": resource_not_found_handler,
#     "request_validation_exception_handler": request_validation_exception_handler,
#     "assert_exception_handler": assert_exception_handler,
# }
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
]
