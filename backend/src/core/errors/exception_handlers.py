import logging
import traceback
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Interface, IPv6Network
from typing import Any, NewType
from uuid import UUID

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.errors import err_codes
from src.core.errors.err_codes import ErrorCode
from src.core.utils.context import locale_ctx, request_id_ctx
from src.core.utils.i18n import _

_E = NewType("_E", Exception)
logger = logging.getLogger(__name__)


def error_message_value_handler(value: Any) -> Any:
    if isinstance(value, dict) and "en" in value:
        return value[locale_ctx.get()]
    if isinstance(value, IPv4Address | IPv6Address | IPv4Network | IPv6Network | IPv4Interface | IPv6Interface | UUID):
        return str(value)
    if isinstance(value, list):
        return [str(_v) for _v in value]
    return value


class TokenInvalidForRefreshError(Exception): ...


class TokenInvalidError(Exception): ...


class TokenExpireError(Exception): ...


class PermissionDenyError(Exception): ...


class NotFoundError(Exception):
    def __init__(self, name: str, field: str, value: Any) -> None:
        self.name = name
        self.field = field
        self.value = error_message_value_handler(value)

    def __repr__(self) -> str:
        return f"Object:{self.name} with field:{self.field}-value:{self.value} not found."


class ExistError(Exception):
    def __init__(self, name: str, field: str, value: Any) -> None:
        self.name = name
        self.field = field
        self.value = error_message_value_handler(value)

    def __repr__(self) -> str:
        return f"Object:{self.name} with field:{self.field}-value:{self.value} already exist."


class GenerError(Exception):
    def __init__(
        self,
        error: ErrorCode,
        params: dict[str, Any] | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.error = error
        self.params = params
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"Gener Error Occurred: ErrCode: {self.error.error}, Message: {self.error.message}"


def log_exception(exception: BaseException, include_traceback: bool) -> None:
    """
    Logs an exception.

    Args:
        exception (BaseException): The exception to be logged.
        include_traceback (bool): Indicates whether to include detailed trace information in the log.

    Returns:
        None
    """
    exception_type = type(exception).__name__
    logger.warning(f"ErrorMessage: {exception}")
    logger.warning(f"Exception Type: {exception_type}")

    if include_traceback:
        traceback_info = "".join(traceback.format_exc().splitlines()[-3:])
        logger.warning(f"Traceback: {traceback_info}")


async def token_invalid_handler(request: Request, exc: TokenInvalidError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, False)
    response_content = err_codes.ERR_10002.dict()
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=response_content)


async def invalid_token_for_refresh_handler(request: Request, exc: TokenInvalidForRefreshError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, False)
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=err_codes.ERR_10004.dict())


async def token_expired_handler(request: Request, exc: TokenExpireError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, False)
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=err_codes.ERR_10003.dict())


async def permission_deny_handler(request: Request, exc: PermissionDenyError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, False)
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=err_codes.ERR_10004.dict())


async def resource_not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, True)
    error_message = _(err_codes.ERR_404.message, name=exc.name, filed=exc.field, value=exc.value)
    content = {"error": err_codes.ERR_404.error, "message": error_message}
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=content)


async def resource_exist_handler(request: Request, exc: ExistError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, True)
    error_message = _(err_codes.ERR_409.message, name=exc.name, filed=exc.field, value=exc.value)
    content = {"error": err_codes.ERR_409.error, "message": error_message}
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=content)


def gener_error_handler(request: Request, exc: GenerError) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error.error,
            "message": _(exc.error.message, **exc.params) if exc.params else _(exc.error.message),
        },
    )


def default_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    log_exception(exc, True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": err_codes.ERR_500.error,
            "message": _(err_codes.ERR_500.message, request_id=request_id_ctx.get()),
        },
    )


exception_handlers = [
    {"exception": TokenInvalidError, "handler": token_invalid_handler},
    {"exception": TokenExpireError, "handler": token_expired_handler},
    {"exception": TokenInvalidForRefreshError, "handler": invalid_token_for_refresh_handler},
    {"exception": PermissionDenyError, "handler": permission_deny_handler},
    {"exception": NotFoundError, "handler": resource_not_found_handler},
    {"exception": ExistError, "handler": resource_exist_handler},
    {"exception": GenerError, "handler": gener_error_handler},
]


sentry_ignore_errors = [
    TokenExpireError,
    TokenInvalidError,
    TokenInvalidForRefreshError,
    PermissionDenyError,
    NotFoundError,
    ExistError,
]
