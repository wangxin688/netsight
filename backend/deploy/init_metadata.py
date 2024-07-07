import json
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from anyio import open_file, run
from sqlalchemy import select

from src.core.config import PROJECT_DIR
from src.core.database.session import async_session
from src.core.utils.context import request_id_ctx, user_ctx
from src.features.admin.models import Group, Role, User
from src.features.admin.security import get_password_hash
from src.features.consts import ReservedRoleSlug
from src.features.intend.models import CircuitType, DeviceRole, DeviceType, IPRole, Manufacturer, Platform
from src.features.ipam.models import Block

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def init_user(session: "AsyncSession") -> None:
    role = (
        await session.scalars(
            select(Role).where(Role.name == "Administrator", Role.slug == ReservedRoleSlug.ADMIN.value)
        )
    ).one_or_none()
    if not role:
        role = Role(
            name="Administrator", slug=ReservedRoleSlug.ADMIN.value, description="Administrator with full authority"
        )
        session.add(role)
        await session.commit()
    group = (
        await session.scalars(select(Group).where(Group.name == "Administrators", Group.role_id == role.id))
    ).one_or_none()
    if not group:
        group = Group(name="Administrators", description="Administrators group", role_id=role.id)
        session.add(group)
        await session.commit()
    user = (
        await session.scalars(
            select(User).where(User.name == "admin", User.email == "admin@netsight.com", User.group_id == group.id)
        )
    ).one_or_none()
    if not user:
        user = User(
            name="admin",
            email="admin@netsight.com",
            password=get_password_hash("admin"),
            group_id=group.id,
            role_id=role.id,
        )
        session.add(user)
        await session.commit()
    user_ctx.set(user.id)


async def init_platform(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/platform.json") as f:
        contents = await f.read()
        platforms = json.loads(contents)
        new_platforms = [Platform(**p) for p in platforms]
        db_objs = (await session.scalars(select(Platform))).all()
        if not db_objs:
            session.add_all(new_platforms)
        else:
            slugs = [p.slug for p in db_objs]
            for new_p in new_platforms:
                if new_p.slug not in slugs:
                    session.add(new_p)
        await session.commit()


async def init_manufacturer(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/manufacturer.json") as f:
        contents = await f.read()
        manufacturers = json.loads(contents)
        new_manufacturers = [Manufacturer(**p) for p in manufacturers]
        db_objs = (await session.scalars(select(Manufacturer))).all()
        if not db_objs:
            session.add_all(new_manufacturers)
        else:
            slugs = [v.slug for v in db_objs]
            for new_v in new_manufacturers:
                if new_v.slug not in slugs:
                    session.add(new_v)
        await session.commit()


async def init_device_type(session: "AsyncSession") -> None:
    path = Path(f"{PROJECT_DIR}/deploy/collectiions/devices_types")
    for file in path.glob("*.json"):
        async with await open_file(file) as f:
            contents = await f.read()
            device_types = json.loads(contents)
            new_device_types = [DeviceType(**d) for d in device_types]
            db_objs = (await session.scalars(select(DeviceType))).all()
            if not db_objs:
                session.add_all(new_device_types)
            else:
                names = [d.name for d in db_objs]
                for new_d in new_device_types:
                    if new_d.name not in names:
                        session.add(new_d)
    await session.commit()


async def init_circuit_type(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/circuit_type.json") as f:
        contents = await f.read()
        circuit_types = json.loads(contents)
        new_circuit_types = [CircuitType(**c) for c in circuit_types]
        db_objs = (await session.scalars(select(CircuitType))).all()
        if not db_objs:
            session.add_all(new_circuit_types)
        else:
            slugs = [c.slug for c in db_objs]
            for new_c in new_circuit_types:
                if new_c.slug not in slugs:
                    session.add(new_c)
        await session.commit()


async def init_device_role(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/device_role.json") as f:
        contents = await f.read()
        device_roles = json.loads(contents)
        new_device_roles = [DeviceRole(**d) for d in device_roles]
        db_objs = (await session.scalars(select(DeviceRole))).all()
        if not db_objs:
            session.add_all(new_device_roles)
        else:
            slugs = [d.slug for d in db_objs]
            for new_d in new_device_roles:
                if new_d.slug not in slugs:
                    session.add(new_d)
        await session.commit()


async def init_ip_role(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/ip_role.json") as f:
        contents = await f.read()
        ip_roles = json.loads(contents)
        new_ip_roles = [IPRole(**i) for i in ip_roles]
        db_objs = (await session.scalars(select(IPRole))).all()
        if not db_objs:
            session.add_all(new_ip_roles)
        else:
            slugs = [i.slug for i in db_objs]
            for new_i in new_ip_roles:
                if new_i.slug not in slugs:
                    session.add(new_i)
        await session.commit()


async def init_block(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/block.json") as f:
        contents = await f.read()
        blocks = json.loads(contents)
        new_blocks = [Block(**b) for b in blocks]
        db_objs = (await session.scalars(select(Block))).all()
        if not db_objs:
            session.add_all(new_blocks)
        else:
            names = [b.name for b in db_objs]
            for new_b in new_blocks:
                if new_b.name not in names:
                    session.add(new_b)
        await session.commit()


async def init_meta() -> None:
    request_id_ctx.set(str(uuid4()))
    async with async_session() as session:
        await init_user(session)
        await init_platform(session)
        await init_manufacturer(session)
        await init_device_type(session)
        await init_circuit_type(session)
        await init_device_role(session)


if __name__ == "__main__":
    run(init_meta)
