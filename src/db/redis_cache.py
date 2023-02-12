import asyncio
from functools import wraps
from typing import Callable

from fastapi import Response

from src.db.redis_session import RedisClient


def cache(*, expire: int = 3600):
    """Cache decorator"""

    def outer(func: Callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            _kwargs = kwargs.copy()
            # request: Request | None = _kwargs.pop("request", None)
            response: Response | None = _kwargs.pop("response", None)
            create_response_directly = not response
            if create_response_directly:
                response = Response()

            redis_cache = RedisClient()
            key = redis_cache.get_cache_key(func, *args, **kwargs)
            ttl, in_cache = await redis_cache.check_cache(key)
            if in_cache:
                redis_cache.set_response_headers(response, True, in_cache, ttl)
                return Response(
                    content=in_cache,
                    media_type="application/json",
                    headers=response.headers,
                )
            response_data = await get_api_response_async(func, *args, **kwargs)
            ttl = expire
            cached = redis_cache.add_to_cache(key, response_data, ttl)
            if cached:
                redis_cache.set_response_headers(response, cache_hit=False, response_data=response_data, ttl=ttl)
                return (
                    Response(
                        content=response_data,
                        media_type="application/json",
                        headers=response.headers,
                    )
                    if create_response_directly
                    else response_data
                )
            return response_data

        return inner

    return outer


async def get_api_response_async(func, *args, **kwargs):
    """Helper function that allows decorator to work with both async and non-async functions."""
    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
