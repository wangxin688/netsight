from typing import TYPE_CHECKING

import pytest
from fastapi import status

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.parametrize(
    "path",
    ["/api/docs", "/api/redoc", "/api/openapi.json", "/api/health", "/api/version", "/api/elements"],
)
async def test_main(client: "AsyncClient", path: str) -> None:
    response = await client.get(path)
    assert response.status_code == status.HTTP_200_OK
