"""
This module define the error code of http response for error handling.
Error_code design rule and code range:
The first code xxxx0 of range as a reserve code for unknown error of service
range: 10000, step 1000 for every sub app/service
Error_code is designed with four fields: code, en_msg, ch_msg, scope
- code: unique return code of api response, type: integer
- msg: unique english return message of api response, type: string
- scope: error code scope for services, all or services leve
* service netisht:              0-10000(reserved)
* service auth:                 10001-11000
"""
from dataclasses import asdict, dataclass
from typing import Any, List

__all__ = (
    "ERR_NUM_0",
    "ERR_NUM_1",
    "ERR_NUM_500",
    "ERR_NUM_4001",
    "ERR_NUM_4002",
    "ERR_NUM_4011",
    "ERR_NUM_4003",
    "ERR_NUM_4004",
    "ERR_NUM_10001",
    "ERR_NUM_10002",
    "ERR_NUM_10003",
    "ERR_NUM_10004",
)


@dataclass(frozen=True)
class ErrCode:
    code: int
    msg: str
    data: Any

    def dict(self):
        return asdict(self)


ERR_NUM_0 = ErrCode(0, "success", None)
ERR_NUM_1 = ErrCode(
    0, "Validation Error, please check requested params or body format", None
)
ERR_NUM_500 = ErrCode(500, "Internal Server Error", None)
ERR_NUM_4001 = ErrCode(
    4001, "Authenticated failed: Bearer token invalid or not provide", None
)
ERR_NUM_4002 = ErrCode(4001, "Authenticated failed: Bearer token expired", None)
ERR_NUM_4011 = ErrCode(4011, "Unauthenticated: Bearer token is refresh token", None)

ERR_NUM_4003 = ErrCode(
    4003, "Permission Denied: Privilege limited, Operation not permit", None
)
ERR_NUM_4004 = ErrCode(4004, "Resource not found: Requested data not existed", None)
ERR_NUM_10001 = ErrCode(10001, "Cannot use this email, already exists", None)
ERR_NUM_10002 = ErrCode(10002, "Incorrect email for user, not found", None)
ERR_NUM_10003 = ErrCode(10003, "Incorrect password", None)
ERR_NUM_10004 = ErrCode(10004, "User not found", None)


def __getattr__(name: str) -> ErrCode:
    raise AttributeError("module {__name__} has not attribute '{name}'")


def get_code_all() -> List[dict]:
    """Get all error code"""
    codes = [
        {"name": k, "value": v.dict()}
        for k, v in globals().items()
        if k.startswith("ERR_NUM")
    ]
    return codes


def __dir__():
    return sorted(list(__all__))
