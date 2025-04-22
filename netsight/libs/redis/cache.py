import asyncio
import logging
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from functools import partial, update_wrapper, wraps
from hashlib import md5
from inspect import Signature, signature
from typing import Any, ParamSpec, TypeVar, get_type_hints

from fastapi import Request, Response
from fastapi.concurrency import run_in_threadpool

from netsight.libs.redis.session import ALWAYS_IGNORE_ARG_TYPES, redis_client

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def _get_cache_key(func: Callable, *args: Any, **kwargs: Any) -> str:
    sig = signature(func)
    type_hints = get_type_hints(func)
    func_args = _get_func_args(sig, *args, **kwargs)
    args_str = ""
    for arg, arg_value in func_args.items():
        if arg in type_hints:
            arg_type = type_hints[arg]
            if arg_type not in ALWAYS_IGNORE_ARG_TYPES:
                args_str += f"{arg}={arg_value}"
    return md5(f"{func.__module__}.{func.__name__}({args_str})".encode()).hexdigest()  # noqa: S324


def _get_func_args(sig: Signature, *args: Any, **kwargs: Any) -> OrderedDict[str, Any]:
    func_args = sig.bind(*args, **kwargs)
    func_args.apply_defaults()
    return func_args.arguments


async def _get_api_response_async(
    func: Callable[P, Awaitable[R]], *args: P.args, **kwargs: P.kwargs
) -> R | Awaitable[R]:
    return (
        await func(*args, **kwargs)
        if asyncio.iscoroutinefunction(func)
        else await run_in_threadpool(func, *args, **kwargs)
    )


def cache(*, expire: int = 600):  # noqa: ANN201
    def outer(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R, Response]]:
        @wraps(func)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> R | Response:
            copy_kwargs = kwargs.copy()
            request: Request | None = copy_kwargs.pop("request", None)
            response: Response | None = copy_kwargs.pop("respinse", None)
            create_response_directly = not response
            if create_response_directly:
                response = Response()
            if redis_client.request_is_not_cacheable(request):
                result = await _get_api_response_async(func, *args, **kwargs)
            key = _get_cache_key(func, *args, **kwargs)
            ttl, in_cache = await redis_client.check_cache(key)
            if in_cache:
                redis_client.set_response_headers(response, True, ttl)
                result = in_cache
            else:
                result = await _get_api_response_async(func, *args, **kwargs)
                cached = await redis_client.add_to_cache(key, result, expire)
                if cached:
                    redis_client.set_response_headers(response, cache_hit=False, ttl=ttl)
            return result

        return inner

    return outer


cache_one_hour = partial(cache, expire=3600)
cache_one_day = partial(cache, expire=86400)

update_wrapper(cache_one_day, cache)
update_wrapper(cache_one_hour, cache)
