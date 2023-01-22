"""
This module define the error code of http response for error handling.
Error_code design rule and code range:
The first code xxxx0 of range as a reserve code for unknown error of service
range: 10000, step 1000 for every sub app/service
Error_code is designed with four fields: code, en_msg, ch_msg, scope
- code: unique return code of api response, type: integer
- msg: unique english return message of api response, type: string
- scope: error code scope for services, all or services level
* service netsight:              0-10000(reserved)
* service auth:                 10001-11000
"""
from typing import Any, Dict, List, NamedTuple, Optional

from pydantic import BaseModel, root_validator

from src.app.netsight.const import LOCALE
from src.utils.i18n_loaders import _

__all__ = (
    "ERR_NUM_422",
    "ERR_NUM_500",
    "ERR_NUM_202",
    "ERR_NUM_401",
    "ERR_NUM_402",
    "ERR_NUM_411",
    "ERR_NUM_403",
    "ERR_NUM_404",
    "ERR_NUM_422",
    "ERR_NUM_10001",
    "ERR_NUM_10002",
    "ERR_NUM_10003",
)


class ResponseMsg(BaseModel):
    code: Optional[int] = 0
    data: Optional[Any] = None
    locale: Optional[LOCALE] = "en_US"
    message: Optional[str] = "netsight.success"

    @root_validator(pre=False)
    def i18n_msg(cls, values):
        if values["code"] == 0:
            _message: str = _(path=values["message"], locale=values["locale"])
            values["message"] = _message
            return values
        return values


class ErrCode(NamedTuple):
    code: int
    message: str


ERR_NUM_422: ErrCode = ErrCode(1, "netsight.validation_error")
ERR_NUM_500: ErrCode = ErrCode(500, "netsight.server_error")
ERR_NUM_202: ErrCode = ErrCode(202, "netsight.in_process")
ERR_NUM_401: ErrCode = ErrCode(401, "auth.token_invalid_not_provided")
ERR_NUM_402: ErrCode = ErrCode(402, "auth.token_expired")
ERR_NUM_411: ErrCode = ErrCode(411, "auth.refresh_token")

ERR_NUM_403: ErrCode = ErrCode(403, "auth.permission_denied")
ERR_NUM_404: ErrCode = ErrCode(404, "netsight.not_found")
ERR_NUM_409: ErrCode = ErrCode(409, "netsight.already_exists")
ERR_NUM_10001: ErrCode = ErrCode(10001, "Cannot use this email, already exists")
ERR_NUM_10002: ErrCode = ErrCode(10002, "Incorrect email for user, not found")
ERR_NUM_10003: ErrCode = ErrCode(10003, "auth.incorrect_password")


def __getattr__(name: str) -> ResponseMsg:
    raise AttributeError(f"module {__name__} has not attribute '{name}'")


def get_code_all(locale: LOCALE) -> List[Dict[str, Any]]:
    """Get all error code"""
    codes = [
        {"code": v.code, "message": _(v.message, locale)}
        for k, v in globals().items()
        if k.startswith("ERR_NUM")
    ]
    return codes


def __dir__() -> list:
    return sorted(list(__all__))


def error_404_409(
    code: ErrCode,
    locale: LOCALE,
    object: str,
    field: str,
    value: Any,
):
    return ResponseMsg(
        code=code.code,
        locale=locale,
        message=_(code.message, locale, object, field, value),
    )
