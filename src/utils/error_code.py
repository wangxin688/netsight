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
    "ERR_NUM_1",
    "ERR_NUM_500",
    "ERR_NUM_2002",
    "ERR_NUM_4001",
    "ERR_NUM_4002",
    "ERR_NUM_4011",
    "ERR_NUM_4003",
    "ERR_NUM_4004",
    "ERR_NUM_4022",
    "ERR_NUM_10001",
    "ERR_NUM_10002",
    "ERR_NUM_10003",
    "ERR_NUM_10004",
    "ERR_NUM_10005",
    "ERR_NUM_10006",
    "ERR_NUM_10007",
    "ERR_NUM_10008",
    "ERR_NUM_10009",
)


class ResponseMsg(BaseModel):
    code: int = 0
    data: Optional[Any] = None
    locale: LOCALE = "en_US"
    message: Optional[str] = "netsight.response_success_msg"

    @root_validator(pre=False)
    def i18n_msg(cls, values):
        _message: str = _(values["message"], values["locale"])
        values["message"] = _message
        return values


class ErrCode(NamedTuple):
    code: int
    message: str


ERR_NUM_1: ErrCode = ErrCode(1, "validation_error")
ERR_NUM_500: ErrCode = ErrCode(500, "server_error")
ERR_NUM_2002: ErrCode = ErrCode(202, "in_process")
ERR_NUM_4001: ErrCode = ErrCode(401, "token_invalid_not_provided")
ERR_NUM_4002: ErrCode = ErrCode(402, "token_expired")
ERR_NUM_4011: ErrCode = ErrCode(411, "refresh_token")

ERR_NUM_4003: ErrCode = ErrCode(403, "permission_denied")
ERR_NUM_4004: ErrCode = ErrCode(404, "Resource not found: Requested data not existed")
ERR_NUM_4009: ErrCode = ErrCode(409, "Resource already exists")
ERR_NUM_4022: ErrCode = ErrCode(422, "Unprocessable Entity")
ERR_NUM_10001: ErrCode = ErrCode(10001, "Cannot use this email, already exists")
ERR_NUM_10002: ErrCode = ErrCode(10002, "Incorrect email for user, not found")
ERR_NUM_10003: ErrCode = ErrCode(10003, "Incorrect password")
ERR_NUM_10004: ErrCode = ErrCode(10004, "User not found")
ERR_NUM_10005: ErrCode = ErrCode(10005, "User with same email already existed")
ERR_NUM_10006: ErrCode = ErrCode(10006, "Group with same name already existed")
ERR_NUM_10007: ErrCode = ErrCode(10007, "Group not found")
ERR_NUM_10008: ErrCode = ErrCode(10008, "Role with same name already existed")
ERR_NUM_10009: ErrCode = ErrCode(10009, "Role not found")


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
