from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from src.utils.error_code import (
    ERR_NUM_1,
    ERR_NUM_500,
    ERR_NUM_4001,
    ERR_NUM_4002,
    ERR_NUM_4003,
    ERR_NUM_4004,
    ERR_NUM_4011,
)
from src.utils.loggers import logger

# class NetSightException(Exception):
#     status_code = 500
#     message = ""

#     def __init__(
#         self,
#         message: str = "",
#         exception: Optional[Exception] = None,
#         error_type: Optional[NetSightErrorType] = None,
#     ):
#         self.message = message or ""
#         self._exception = exception
#         self._error_type = error_type
#         super().__init__(self.message)

#     @property
#     def error_type(self) -> Optional[NetSightErrorType]:
#         return self._error_type

#     def dict(self) -> dict[str, Any]:
#         result = {}
#         if hasattr(self, "message"):
#             result["message"] = self.message
#         if self.error_type:
#             result["error_type"] = self.error_type
#         if self.exception is not None and hasattr(self.exception, "dict"):
#             result = {**result, **self.exception.dict()}
#         return result


class TokenNotProvidedError(Exception):
    pass


class TokenInvalidError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


class TokenInvalidForRefreshError(Exception):
    pass


class PermissionDenyError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class BadQueryFormat(Exception):
    pass


class MissingSessionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SessionNotInitError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


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


async def user_not_found_handler(
    request: Request, exc: UserNotFoundError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_200_OK, content=ERR_NUM_4004._asdict()
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


async def request_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    return_info = ERR_NUM_500.dict()
    return_info.update({"data": jsonable_encoder(str(exc))})
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=return_info)
