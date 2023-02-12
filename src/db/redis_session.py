import json
from typing import Any, Dict, Tuple

import redis.asyncio as redis
from fastapi import Request, Response

from src.core.config import settings

DEFAULT_RESPONSE_HEADER = "X-Cache"


async def init_redis_pool(db: int) -> redis.Redis:
    redis_c = await redis.from_url(settings.REDIS_DSN, encoding="utf-8", db=db, decode_responses=True)
    return redis_c


class RedisClient:
    def __init__(self, redis: redis.Redis, response_header: str | None = DEFAULT_RESPONSE_HEADER) -> None:
        self._redis = redis
        self.response_header = response_header

    async def set_cache(self, key: str, data: Any, expire: int = 1800):
        return await self._redis.set(key, json.dumps(data), ex=expire)

    async def get_cache(self, key: str) -> Dict[str, Any]:
        result = await self._redis.get(key)
        if result:
            return json.loads(result)
        return result

    async def delete_cache(self, key: str):
        return await self._redis.delete(key)

    async def ttl(self, key):
        return await self.r.ttl(key)

    def request_is_cacheable(self, request: Request) -> bool:
        _cache = request.headers.get("Cache-Control", "")
        if _cache != "no-cache":
            return request and False
        return request and True

    def set_response_headers(
        self,
        response: Response,
        cache_hit: bool,
        response_data: Dict = None,
        ttl: int = None,
    ) -> None:
        response.headers[self.response_header] = "Hit" if cache_hit else "Miss"
        response.headers["Cache-Control"] = f"max-age={ttl}"

    async def check_cache(self, key: str) -> Tuple[int, str]:
        pipe = await self._redis.pipeline()
        ttl, in_cache = pipe.ttl(key).get(key).execute()
        return (ttl, in_cache)

    # async def pubsub
