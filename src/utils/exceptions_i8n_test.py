from typing import Any

from fastapi_babel import _

__all__ = (
    "TokenNotProvidedError",
    "TokenInvalidError",
    "TokenExpiredError",
    "TokenInvalidForRefreshError",
    "PermissionDenyError",
    "ResourceNotFoundError",
)


INTERNAL_SERVER_ERROR_CODE = 500
LOGMSG_ERR_SEC_ACCESS_DENIED = "Access is Denied for: {0} on: {1}"


class NetSightException(Exception):
    def __init__(
        self, code: int = 500, data: Any = None, msg: str = _("internal server error")
    ) -> None:
        self.code = code
        self.data = data
        self.msg = msg

    def __str__(self):
        return self.msg

    def dict(self):
        return {"code": self.code, "data": self.data, "msg": self.msg}


class TokenNotProvidedError(NetSightException):
    msg = "Token not provided"


class TokenInvalidError(NetSightException):
    pass


class TokenExpiredError(NetSightException):
    pass


class TokenInvalidForRefreshError(NetSightException):
    pass


class PermissionDenyError(NetSightException):
    pass


class ResourceNotFoundError(NetSightException):
    def __init__(
        self, code: int = 4004, data=None, msg: str = "request resource not found"
    ) -> None:
        self.code = code
        self.data = data
        self.msg = msg

    def __str__(self):
        return self.msg

    def dict(self):
        return {"code": self.code, "data": self.data, "msg": self.msg}


print(TokenNotProvidedError)
