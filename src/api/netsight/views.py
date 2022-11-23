from celery.result import AsyncResult
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from src.api import deps
from src.auth.models import User
from src.utils.error_code import ERR_NUM_0, ERR_NUM_500, ERR_NUM_2002

router = APIRouter()


@router.get("/tasks/result/{task_id}")
async def get_task_result(
    task_id: str, current_user: User = Depends(deps.get_current_user)
):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=200, content=ERR_NUM_2002._asdict())
    state = task.state
    if state == "FAILURE":
        traceback_info = task.traceback
        logger.error(f"celery task id: {task_id} execute failed" + traceback_info)
        error_msg = task.result
        return_info = ERR_NUM_500._asdict()
        return_info.update({"data": error_msg})
        return JSONResponse(status_code=200, content=return_info)
    result = task.get()

    return {
        "code": ERR_NUM_0.code,
        "data": {"task_id": str(task_id), "results": result},
        "msg": ERR_NUM_0.msg,
    }
