import asyncio
from functools import wraps
from typing import Callable

import httpx
from uplink.clients import exceptions, interfaces, io

ssl_context = httpx.create_ssl_context()


def thread_callback(callback: Callable):
    @wraps(callback)
    async def _callback(*args, **kwargs):
        return callback(*args, **kwargs)

    return _callback


class HttpxClient(interfaces.HttpClientAdapter):
    exceptions = exceptions.Exceptions()

    def __init__(self, session=None, verify=False, **kwargs):
        self._session = session or httpx.AsyncClient(verify=ssl_context if verify else False, **kwargs)
        self._sync_callback_adapter = thread_callback

    def __del__(self):
        try:
            if not self._session.is_closed:
                asyncio.create_task(self._session.aclose())
        except RuntimeError:
            pass

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._session.__aexit__()

    def warp_callback(self, callback):
        if not asyncio.iscoroutinefunction(callback):
            callback = self._sync_callback_adapter(callback)
        return callback

    def apply_callback(self, callback, response):
        return self.warp_callback(callback)(response)

    @staticmethod
    def io():
        return io.AsyncioStrategy()


HttpxClient.exceptions.BaseClientException = httpx.HTTPStatusError
HttpxClient
