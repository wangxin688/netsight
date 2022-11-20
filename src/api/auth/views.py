from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from src.utils.loggers import logger

auth_router = APIRouter(default_response_class=ORJSONResponse)


@auth_router.post("/login")
def login():
    pass


@auth_router.get("/item")
async def get_abc(a, b):
    assert isinstance(a, int), "bad type"
    logger.info(f"receive: {a}, {b}")
    return a + b


@auth_router.get("/test")
async def log_test(a: int, b: int):
    logger.info(f"receive {a} {b}")
    res = a / b
    return res
