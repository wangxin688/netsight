import json
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from anyio import open_file, run

from src.config import PROJECT_DIR
from src.consts import ReservedRoleSlug
from src.context import request_id_ctx, user_ctx
from src.db import Block, CircuitType, DeviceRole, DeviceType, Group, IPRole, Platform, RackRole, Role, User, Vendor
from src.db.session import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def init_user(session: "AsyncSession") -> None:
    new_role = Role(
        name="Administrator", slug=ReservedRoleSlug.ADMIN.value, description="Administrator with full authority"
    )
    session.add(new_role)
    await session.commit()
    new_group = Group(name="Administrators", description="Administrators group", role_id=new_role.id)
    session.add(new_group)
    await session.commit()
    new_user = User(
        name="admin",
        email="admin@netsight.com",
        password="admin",  # noqa: S106
        group_id=new_group.id,
        role_id=new_role.id,
    )
    session.add(new_user)
    await session.commit()
    user_ctx.set(new_user.id)


async def init_platform(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/platform.json") as f:
        contents = await f.read()
        platforms = json.loads(contents)
        new_platforms = [Platform(**p) for p in platforms]
        session.add_all(new_platforms)
        await session.commit()


async def init_vendor(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/vendor.json") as f:
        contents = await f.read()
        vendors = json.loads(contents)
        new_vendors = [Vendor(**p) for p in vendors]
        session.add_all(new_vendors)
        await session.commit()


async def init_device_type(session: "AsyncSession") -> None:
    path = Path(f"{PROJECT_DIR}/deploy/collectiions/devices_types")
    for file in path.glob("*.json"):
        async with await open_file(file) as f:
            contents = await f.read()
            device_types = json.loads(contents)
            new_device_types = [DeviceType(**d) for d in device_types]
            session.add_all(new_device_types)
    await session.commit()


async def init_circuit_type(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/circuit_type.json") as f:
        contents = await f.read()
        circuit_types = json.loads(contents)
        new_circuit_types = [CircuitType(**c) for c in circuit_types]
        session.add_all(new_circuit_types)
        await session.commit()


async def init_device_role(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/device_role.json") as f:
        contents = await f.read()
        device_roles = json.loads(contents)
        new_device_roles = [DeviceRole(**d) for d in device_roles]
        session.add_all(new_device_roles)
        await session.commit()


async def init_rack_role(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/rack_role.json") as f:
        contents = await f.read()
        rack_roles = json.loads(contents)
        new_rack_roles = [RackRole(**r) for r in rack_roles]
        session.add_all(new_rack_roles)
        await session.commit()


async def init_ip_role(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/ip_role.json") as f:
        contents = await f.read()
        ip_roles = json.loads(contents)
        new_ip_roles = [IPRole(**i) for i in ip_roles]
        session.add_all(new_ip_roles)
        await session.commit()


async def init_block(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/block.json") as f:
        contents = await f.read()
        blocks = json.loads(contents)
        new_blocks = [Block(**b) for b in blocks]
        session.add_all(new_blocks)
        await session.commit()


async def init_meta() -> None:
    request_id_ctx.set(str(uuid4()))
    async with async_session() as session:
        await init_user(session)
        await init_platform(session)
        await init_vendor(session)
        await init_device_type(session)
        await init_circuit_type(session)
        await init_device_role(session)
        await init_rack_role(session)


if __name__ == "__main__":
    run(init_meta)
