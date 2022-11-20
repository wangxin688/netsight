from fastapi import APIRouter, Depends

from src.api.base import BaseResponse
from src.api.deps import audit_request
from src.register.middleware import AuditRoute
from src.utils.loggers import logger

router = APIRouter(route_class=AuditRoute)


# @router.post("/login")
# def login():
#     pass


@router.get("/item", response_model=BaseResponse[int])
async def get_abc(a: int, b: int, audit=Depends(audit_request)):
    assert isinstance(a, int), "bad type"
    logger.info(f"receive: {a}, {b}")
    return {"code": 0, "data": a + b, "msg": "success"}


@router.get("/test", response_model=BaseResponse[int])
async def log_test(a: int, b: int, audit=Depends(audit_request)):
    logger.info(f"receive {a} {b}")
    res = a / b
    return {"code": 0, "data": res, "msg": "success"}
