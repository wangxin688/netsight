import json
import logging
from collections.abc import Mapping
from datetime import datetime
from enum import IntEnum, StrEnum
from inspect import Parameter
from typing import Any, NewType, ParamSpec, TypeVar
from uuid import UUID

from fastapi import Request, Response
from httpx import AsyncClient, Client
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import redis.asyncio as redis
from redis import Redis
from netsight.features.admin.models import User

P = ParamSpec("P")
R = TypeVar("R")

DEFAULT_CACHE_HEADER = "X-Cache"
logger = logging.getLogger(__name__)

_T = NewType("_T", BaseModel)
type ArgType = type[object]
SigParameters = Mapping[str, Parameter]
ALWAYS_IGNORE_ARG_TYPES = [Response, Request, Client, AsyncClient, Session, AsyncSession, Redis, User]


class RedisDBType(IntEnum):
    DEFAULT = 0
    CELERY = 1
    PUBSUB = 2


class CacheNamespace(StrEnum):
    API_CACHE = "api_"
    NORMAL_CACHE = "nc_"
    ROLE_CACHE = "role_"


class RedisStatus(IntEnum):
    NONE = 0
    CONNECTED = 1
    AUTH_ERROR = 2
    CONN_ERROR = 3


class RedisEvent(IntEnum):
    CONNECT_BEGIN = 1
    CONNECT_SUCCESS = 2
    CONNECT_FAIL = 3
    KEY_ADDED_TO_CACHE = 4
    KEY_NOT_FOUND_CACHE = 5
    FAILED_TO_CACHE_KEY = 6


def default(obj: Any) -> Any:
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return datetime.strftime(obj, "%Y-%m-%dT%H:%M:%S.%f2")
    return None


class FastapiCache(redis.Redis):
    response_header: str = DEFAULT_CACHE_HEADER
    ignore_arg_types: list[ArgType] = ALWAYS_IGNORE_ARG_TYPES

    async def set_ex(self, name: str, value: Any, expire: int = 1800, namespace: CacheNamespace | None = None) -> Any:
        key = name
        if namespace:
            key = namespace + name
        return self.setex(name=key, time=expire, value=json.dumps(value))

    async def set_nx(self, name: str, value: Any, namespace: CacheNamespace | None = None) -> Any:
        key = name
        if namespace:
            key = namespace + name
        return await self.setnx(name=key, value=json.dumps(value, default=default))

    async def get_cache(self, name: str, namespace: CacheNamespace | None = None) -> Any:
        key = name
        if namespace:
            key = namespace + name
        result = await self.get(name=key)
        if result:
            return json.loads(result)
        return None

    def log(self, event: RedisEvent, msg: str | None = None, name: str | None = None, value: Any = None) -> None:
        message = f"| {event.name}"
        if msg:
            message += "f: {msg}"
        if name:
            message += f": name={name}"
        if value:
            message += f", value={value}"
        logger.info(message)

    @staticmethod
    def request_is_not_cacheable(request: Request) -> bool:
        return request.method not in ["GET"] or any(
            directive in request.headers.get(DEFAULT_CACHE_HEADER, "")
            for directive in ["no-store", "no-cache", "must-revalidate"]
        )

    async def add_to_cache(self, name: str, value: dict | _T, expire: int) -> bool:
        response_data = None
        try:
            response_data = value.model_dump() if isinstance(value, BaseModel) else value
        except TypeError:
            message = f"Object of type {type(value)} is not JSON-serializable"
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, msg=message, name=name, value=value)
            return False
        cached = await self.set_ex(name, response_data, expire, namespace=CacheNamespace.API_CACHE)
        if cached:
            self.log(event=RedisEvent.KEY_ADDED_TO_CACHE, name=name)
        else:
            self.log(event=RedisEvent.FAILED_TO_CACHE_KEY, name=name, value=value)
        return cached

    async def check_cache(self, name: str) -> tuple[int, str]:
        pipe = self.pipeline()
        pipe.ttl(CacheNamespace.API_CACHE + name).get(CacheNamespace.API_CACHE + name)
        ttl, in_cache = await pipe.execute()
        return ttl, json.loads(in_cache) if in_cache else None

    def set_response_headers(self, response: Response, cache_hit: bool, ttl: int | None = None) -> None:
        response.headers[self.response_header] = "Hit" if cache_hit else "Miss"
        response.headers[self.response_header + "-TTL"] = f"max-age-{ttl}"


redis_client: FastapiCache = None
