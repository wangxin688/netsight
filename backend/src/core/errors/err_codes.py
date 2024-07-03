from typing import Any, NamedTuple


class ErrorCode(NamedTuple):
    error: int
    message: str
    details: list[Any] | None = None

    def dict(self):  # noqa: ANN201
        return self._asdict()


# ---------- error code range ----------------


ERR_404 = ErrorCode(404, "app.not_found")
ERR_409 = ErrorCode(409, "app.already_exist")
ERR_500 = ErrorCode(500, "app.internal_server_error")


ERR_10001 = ErrorCode(10001, "admin.user_password_can_not_be_null")
ERR_10002 = ErrorCode(10002, "admin.token_invalid")
ERR_10003 = ErrorCode(10003, "admin.token_expired")
ERR_10004 = ErrorCode(10004, "admin.token_invalid_for_refresh")
ERR_10005 = ErrorCode(10005, "admin.permission_deny")


ERR_20001 = ErrorCode(20001, "admin.user_not_found")
