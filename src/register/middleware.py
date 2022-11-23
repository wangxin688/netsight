import json
import time
import traceback
from typing import Callable

import aiofiles
from asgi_correlation_id import correlation_id
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from src.utils.loggers import logger


class AuditRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def audit_handler(request: Request) -> Response:
            start_time = time.time()
            try:
                response: Response = await original_route_handler(request)
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                response = JSONResponse(
                    status_code=200,
                    content={
                        "code": 500,
                        "data": str(e),
                        "msg": "Internal server error",
                    },
                )
            finally:
                body_ = await request.body()
                body_ = json.loads(body_) if body_ else ""
                if body_ is not None:
                    if body_.get("password"):
                        body_ = ""
                process_time = time.time() - start_time
                response.headers["X-Response-Time"] = str(process_time)
                data = {
                    "x-process-time": process_time,
                    "ip": request.client.host,
                    "method": request.method,
                    "body": body_,
                    "path": request.url.path,
                    "path_params": request.path_params,
                    "query_params": request.query_params._dict,
                    "code": response.status_code,
                    "x-request-id": correlation_id.get(),
                }
                if request.query_params.get("audit"):
                    rsp_data = json.loads(response.body.decode("utf-8"))
                    data.update(
                        {
                            "request_user": request.state.current_user
                            if hasattr(request.state, "current_user")
                            else "",
                            "code": rsp_data.get("code"),
                            "data": rsp_data.get("data"),
                            "msg": rsp_data.get("msg"),
                        }
                    )
                logger.info(data)
                async with aiofiles.open(
                    "log/audit.json", mode="a+", encoding="utf-8"
                ) as f:
                    await f.write(json.dumps(data))
                    await f.write("\n")
                return response

        return audit_handler
