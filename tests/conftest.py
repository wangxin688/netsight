import asyncio
import gc
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

from netsight.app import app
from netsight.core.config import settings
from netsight.core.database.session import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.set_debug(True)
    yield loop
    gc.collect()
    loop.close()


@pytest.fixture(scope="session")
async def admin_token() -> dict[str, str]:
    async with AsyncClient(app=app, base_url=settings.BASE_URL) as client:
        response = await client.post(
            "/api/admin/pwd-login", data={"username": "admin@netsight.com", "password": "admin"}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(scope="session")
async def client(admin_token: dict[str, str]) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=settings.BASE_URL, headers=admin_token) as client:
        yield client


@pytest.fixture(scope="module")
async def session() -> AsyncGenerator["AsyncSession", None]:
    async with async_session() as session:
        yield session
