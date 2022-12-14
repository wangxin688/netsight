from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.app import deps
from src.app.auth.models import User
from src.app.base import BaseListResponse
from src.app.netsight import schemas
from src.utils.error_code import ERR_NUM_500, ERR_NUM_2002, ResponseMsg

router = APIRouter()


@router.get("/tasks/result/{task_id}")
async def get_task_result(
    task_id: str, current_user: User = Depends(deps.get_current_user)
):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=200, content=ERR_NUM_2002.dict())
    state = task.state
    if state == "FAILURE":
        traceback_info = task.traceback
        logger.error(f"celery task id: {task_id} execute failed" + traceback_info)
        error_msg = task.result
        return_info = ERR_NUM_500.dict()
        return_info.update({"data": error_msg})
        return JSONResponse(status_code=200, content=return_info)
    result = task.get()

    return_info = ResponseMsg(data={"task_id": str(task_id), "results": result})
    return return_info


@router.get(
    "/netsight/endpoints", response_model=BaseListResponse[List[schemas.Endpoint]]
)
def inspect_endpoints(request: Request):
    endpoints = [
        {"name": route.name, "url": route.path, "action": route.methods}
        for route in request.app.routes
    ]
    return_info = ResponseMsg(data={"count": len(endpoints), "results": endpoints})
    return return_info
