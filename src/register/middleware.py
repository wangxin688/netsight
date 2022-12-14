import json
import time
from typing import Callable

import aiofiles
from asgi_correlation_id import correlation_id
from fastapi import Request, Response
from fastapi.routing import APIRoute
from loguru import logger


class AuditRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def audit_handler(request: Request) -> Response:
            start_time = time.time()
            response: Response = await original_route_handler(request)
            body_ = None
            try:
                body_ = await request.json()
            except Exception:
                pass
            process_time = time.time() - start_time
            response.headers["X-Response-Time"] = str(process_time)
            data = {
                "x-process-time": process_time,
                "ip": request.client.host,
                "method": request.method,
                "body": body_,
                "path": request.url.path,
                "path_params": request.path_params,
                "query_params": str(request.query_params),
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
