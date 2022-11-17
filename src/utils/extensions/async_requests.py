from typing import Literal

import httpx

from src.utils.loggers import logger


async def async_http_req(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    url: str,
    headers: dict = None,
    payload: dict = None,
):
    async with httpx.AsyncClient() as client:
        try:
            logger.info(
                f"Request start: url: {url}, method: {method}, headers: {headers}, payload: {payload}"
            )
            resp = await client.request(
                method=method, url=url, headers=headers, data=payload
            )
        except httpx.RequestError as e:
            logger.error(f"{url} request failed, {e}")
        assert resp.status_code in [200, 201], resp.text
        logger.info(f"{url} return code={resp.status_code}, info={resp.text}")
        return resp
