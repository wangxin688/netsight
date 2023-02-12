from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Request
from loguru import logger

from src.app import deps
from src.app.auth.models import User
from src.app.base import BaseListResponse
from src.app.deps import get_locale
from src.app.netsight import schemas
from src.utils.error_code import ERR_NUM_202, ERR_NUM_500, ResponseMsg, get_code_all
from src.utils.i18n_loaders import _

router = APIRouter()


@router.get("/tasks/{task_id}")
async def get_task_result(
    task_id: str,
    current_user: User = Depends(deps.get_current_user),
    locale=Depends(get_locale),
):
    task = AsyncResult(task_id)
    if not task.ready():
        return ResponseMsg(
            code=ERR_NUM_202.code,
            data=None,
            locale=locale,
            message=_(ERR_NUM_202.message),
        )
    state = task.state
    if state == "FAILURE":
        traceback_info = task.traceback
        logger.error(f"celery task id: {task_id} execute failed" + traceback_info)
        error_msg = task.result
        return ResponseMsg(
            code=ERR_NUM_500.code,
            data=error_msg,
            locale=locale,
            message=_(ERR_NUM_500.message),
        )
    result = task.get()

    return_info = ResponseMsg(data={"task_id": str(task_id), "results": result}, locale=locale)
    return return_info


@router.get("/endpoints", response_model=BaseListResponse[List[schemas.Endpoint]])
def inspect_endpoints(request: Request, locale=Depends(get_locale)):
    endpoints = [{"name": route.name, "url": route.path, "action": route.methods} for route in request.app.routes]
    return_info = ResponseMsg(data={"count": len(endpoints), "results": endpoints}, locale=locale)
    return return_info


@router.get("/errorcodes")
def get_error_codes(locale=Depends(get_locale)):
    codes = get_code_all(locale=locale)
    return codes
