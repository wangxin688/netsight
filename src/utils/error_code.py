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
from typing import Any, List, Optional

from pydantic import BaseModel

__all__ = (
    "ERR_NUM_0",
    "ERR_NUM_1",
    "ERR_NUM_500",
    "ERR_NUM_2002",
    "ERR_NUM_4001",
    "ERR_NUM_4002",
    "ERR_NUM_4011",
    "ERR_NUM_4003",
    "ERR_NUM_4004",
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


class ErrCode(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None

    def __init__(self, code, msg, data=None) -> None:
        super().__init__(code=code, msg=msg, data=data)


ERR_NUM_0 = ErrCode(0, "success")
ERR_NUM_1 = ErrCode(0, "Validation Error, please check requested params or body format")
ERR_NUM_500 = ErrCode(500, "Internal Server Error")
ERR_NUM_2002 = ErrCode(2002, "Request not completed, in processing")
ERR_NUM_4001 = ErrCode(
    4001, "Authenticated failed: Bearer token invalid or not provide"
)
ERR_NUM_4002 = ErrCode(4001, "Authenticated failed: Bearer token expired")
ERR_NUM_4011 = ErrCode(4011, "Unauthenticated: Bearer token is refresh token")

ERR_NUM_4003 = ErrCode(
    4003, "Permission Denied: Privilege limited, Operation not permit"
)
ERR_NUM_4004 = ErrCode(4004, "Resource not found: Requested data not existed")
ERR_NUM_10001 = ErrCode(10001, "Cannot use this email, already exists")
ERR_NUM_10002 = ErrCode(10002, "Incorrect email for user, not found")
ERR_NUM_10003 = ErrCode(10003, "Incorrect password")
ERR_NUM_10004 = ErrCode(10004, "User not found")
ERR_NUM_10005 = ErrCode(10005, "User with same email already existed")
ERR_NUM_10006 = ErrCode(10006, "Group with same name already existed")
ERR_NUM_10007 = ErrCode(10007, "Group not found")
ERR_NUM_10008 = ErrCode(10008, "Role with same name already existed")
ERR_NUM_10009 = ErrCode(10009, "Role not found")


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
