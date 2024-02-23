import asyncio
import gc
import typing as t

import pytest


@pytest.fixture(scope="session")
def event_loop() -> t.Generator:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    loop.set_debug(enabled=True)
    yield loop
    gc.collect()
    loop.close()
