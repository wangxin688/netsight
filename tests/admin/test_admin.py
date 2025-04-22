from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_operation_id_define(client: "AsyncClient") -> None:
    results = await client.post("/api/admin/permissions")

    assert results.status_code == 200

    permissions = await client.get("/api/admin/permissions")

    assert permissions.status_code == 200
    assert len(permissions.json()) > 0
