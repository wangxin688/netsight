import json
from pathlib import Path
from typing import TYPE_CHECKING

from anyio import open_file, run

from src.circuit.models import CircuitType, DeviceRole, IPRole, RackRole
from src.config import PROJECT_DIR
from src.db.session import async_session
from src.dcim.models import DeviceType, Platform, Vendor

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


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


async def init_device_types(session: "AsyncSession") -> None:
    path = Path(f"{PROJECT_DIR}/deploy/collectiions/devices_types")
    for file in path.glob("*.json"):
        async with await open_file(file) as f:
            contents = await f.read()
            device_types = json.loads(contents)
            new_device_types = [DeviceType(**d) for d in device_types]
            session.add_all(new_device_types)
    await session.commit()


async def init_circuit_types(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/circuit_types.json") as f:
        contents = await f.read()
        circuit_types = json.loads(contents)
        new_circuit_types = [CircuitType(**c) for c in circuit_types]
        session.add_all(new_circuit_types)
        await session.commit()


async def init_device_roles(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/device_roles.json") as f:
        contents = await f.read()
        device_roles = json.loads(contents)
        new_device_roles = [DeviceRole(**d) for d in device_roles]
        session.add_all(new_device_roles)
        await session.commit()


async def init_rack_roles(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/rack_roles.json") as f:
        contents = await f.read()
        rack_roles = json.loads(contents)
        new_rack_roles = [RackRole(**r) for r in rack_roles]
        session.add_all(new_rack_roles)
        await session.commit()


async def init_ip_roles(session: "AsyncSession") -> None:
    async with await open_file(f"{PROJECT_DIR}/deploy/collections/metadata/ip_roles.json") as f:
        contents = await f.read()
        ip_roles = json.loads(contents)
        new_ip_roles = [IPRole(**i) for i in ip_roles]
        session.add_all(new_ip_roles)
        await session.commit()


async def init_meta() -> None:
    async with async_session() as session:
        await init_platform(session)
        await init_vendor(session)
        await init_device_types(session)
        await init_circuit_types(session)
        await init_device_roles(session)
        await init_rack_roles(session)


if __name__ == "__main__":
    run(init_meta)
