from collections.abc import Sequence
from typing import TYPE_CHECKING

from src.consts import DeviceStatus, RackStatus
from src.db.dtobase import DtoBase
from src.dcim import schemas
from src.dcim.models import Device, DeviceType, Rack
from src.dcim.schemas import DeviceCreate, RackCreate, RackUpdate
from src.org.models import Location
from src.org.services import LocationDto

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("RackDto",)


class RackDto(DtoBase[Rack, schemas.RackCreate, schemas.RackUpdate, schemas.RackQuery]):
    async def create(
        self,
        session: "AsyncSession",
        obj_in: RackCreate,
        excludes: set[str] | None = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        commit: bool | None = True,
    ) -> Rack:
        loc_dto = LocationDto(Location)
        if obj_in.location_id and obj_in.site_id:
            await loc_dto.location_compatible(session, obj_in.location_id, obj_in.site_id)
        if obj_in.location_id and not obj_in.site_id:
            db_loc = await loc_dto.get_one_or_404(session, obj_in.location_id)
            obj_in.site_id = db_loc.site_id
        return await super().create(session, obj_in, excludes, exclude_unset, exclude_none, commit)

    async def update(
        self,
        session: "AsyncSession",
        db_obj: Rack,
        obj_in: RackUpdate,
        excludes: set[str] | None = None,
        commit: bool | None = True,
    ) -> Rack:
        loc_dto = LocationDto(Location)
        if obj_in.location_id and obj_in.site_id:
            await loc_dto.location_compatible(session, obj_in.location_id, obj_in.site_id)
        elif obj_in.location_id and not obj_in.site_id:
            await loc_dto.location_compatible(session, obj_in.location_id, db_obj.site_id)
        elif not obj_in.location_id and obj_in.site_id and db_obj.location_id:
            await loc_dto.location_compatible(session, db_obj.location_id, obj_in.site_id)
        await self.update_rack_device_status(session, obj_in, db_obj.id)
        return await super().update(session, db_obj, obj_in, excludes, commit)

    async def get_rack_devices(self, session: "AsyncSession", rack_id: int) -> Sequence["Device"]:
        device_dto = DeviceDto(Device)
        stmt = device_dto._get_base_stmt().where(Device.rack_id == rack_id)  # noqa: SLF001
        return (await session.scalars(stmt)).all()

    async def update_rack_device_status(self, session: "AsyncSession", rack: schemas.RackUpdate, pk_id: int) -> None:
        if rack.status == RackStatus.Offline.value:
            devices = await self.get_rack_devices(session, pk_id)
            for device in devices:
                device.status = DeviceStatus.Offline
                session.add(device)


class DeviceDto(DtoBase[Device, schemas.DeviceCreate, schemas.DeviceUpdate, schemas.DeviceQuery]):
    async def create(
        self,
        session: "AsyncSession",
        obj_in: DeviceCreate,
        excludes: set[str] | None = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        commit: bool | None = False,
    ) -> Device:
        loc_dto = LocationDto(Location)
        if obj_in.location_id and obj_in.site_id:
            await loc_dto.location_compatible(session, obj_in.location_id, obj_in.site_id)
        if obj_in.location_id and not obj_in.site_id:
            db_loc = await loc_dto.get_one_or_404(session, obj_in.location_id)
            obj_in.site_id = db_loc.site_id
        device_type_dto = DtoBase(DeviceType)
        db_dt = await device_type_dto.get_one_or_404(session, obj_in.device_type_id)
        new_device = await super().create(session, obj_in, excludes, exclude_unset, exclude_none, commit)
        new_device.platform_id = db_dt.platform_id
        new_device.vendor_id = db_dt.vendor_id
        return await self.commit(session, new_device)

    async def update(
        self,
        session: "AsyncSession",
        db_obj: Device,
        obj_in: schemas.DeviceUpdate,
        excludes: set[str] | None = None,
        commit: bool | None = True,
    ) -> Device:
        if excludes is None:
            excludes = {"device_type_id"}
        loc_dto = LocationDto(Location)
        if obj_in.location_id and obj_in.site_id:
            await loc_dto.location_compatible(session, obj_in.location_id, obj_in.site_id)
        elif obj_in.location_id and not obj_in.site_id:
            await loc_dto.location_compatible(session, obj_in.location_id, db_obj.site_id)
        elif not obj_in.location_id and obj_in.site_id and db_obj.location_id:
            await loc_dto.location_compatible(session, db_obj.location_id, obj_in.site_id)
        if obj_in.device_type_id and obj_in.device_type_id != db_obj.device_type_id:
            device_type_dto = DtoBase(DeviceType)
            db_dt = await device_type_dto.get_one_or_404(session, obj_in.device_type_id)
            db_obj.device_type_id = obj_in.device_type_id
            db_obj.platform_id = db_dt.platform_id
            db_obj.vendor_id = db_dt.vendor_id
        return await super().update(session, db_obj, obj_in, excludes, commit)
