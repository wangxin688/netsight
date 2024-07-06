from typing import TYPE_CHECKING

from src.core.repositories import BaseRepository
from src.features.consts import DeviceRoleSlug, DeviceStatus
from src.features.dcim import schemas
from src.features.dcim.models import Device
from src.features.intend.services import device_role_service
from src.features.org.services import location_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("device_service",)


class DeviceService(BaseRepository[Device, schemas.DeviceCreate, schemas.DeviceUpdate, schemas.DeviceQuery]):
    async def validate_location_and_site(self, session: "AsyncSession", location_id: int, site_id: int) -> None:
        location_site_id = await location_service.get_location_site_id(session, location_id)
        if location_site_id != site_id:
            raise ValueError("location and site must be in the same site")

    async def valiate_create(self, session: "AsyncSession", obj_in: schemas.DeviceCreate) -> schemas.DeviceCreate:
        device_role = await device_role_service.get_one_or_404(session, obj_in.device_role_id)
        if device_role.slug != DeviceRoleSlug.ap:
            obj_in.ap_mode = None
            obj_in.associated_wac_ip = None
            obj_in.ap_group = None
        if obj_in.location_id:
            site_id = await location_service.get_location_site_id(session, obj_in.location_id)
            if obj_in.site_id:
                site_id = await location_service.get_location_site_id(session, obj_in.location_id)
                obj_in.site_id = site_id
        return obj_in

    async def validate_update(
        self, session: "AsyncSession", db_obj: Device, obj_in: schemas.DeviceUpdate
    ) -> schemas.DeviceUpdate:
        location_id, site_id = db_obj.location_id, db_obj.site_id
        for key, value in obj_in.model_dump(exclude_unset=True).items():
            if key in ["location_id", "site_id"]:
                if key == "location_id":
                    location_id = value
                if key == "site_id":
                    site_id = value
            elif key == "device_role_id":
                if value != db_obj.device_role_id:
                    device_role = await device_role_service.get_one_or_404(session, value)
                    if device_role.slug != DeviceRoleSlug.ap:
                        obj_in.ap_mode = None
                        obj_in.associated_wac_ip = None
                        obj_in.ap_group = None
        if location_id and site_id:
            await self.validate_location_and_site(session, location_id, site_id)
        return obj_in

    async def create(
        self,
        session: "AsyncSession",
        obj_in: schemas.DeviceCreate,
        excludes: set[str] | None = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        commit: bool | None = True,
    ) -> Device:
        obj_in = await self.valiate_create(session, obj_in)
        return await super().create(session, obj_in, excludes, exclude_unset, exclude_none, commit)

    async def update(
        self,
        session: "AsyncSession",
        db_obj: Device,
        obj_in: schemas.DeviceUpdate,
        excludes: set[str] | None = None,
        commit: bool | None = True,
    ) -> Device:
        obj_in = await self.validate_update(session, db_obj, obj_in)
        return await super().update(session, db_obj, obj_in, excludes, commit)


class DeviceScrapeService:
    def __init__(self, device_id: int, session: "AsyncSession") -> None:
        self.device_id = device_id
        self.session = session

    async def validate_device(self) -> "Device":
        device = await device_service.get_one_or_404(self.session, self.device_id)
        if device.status != DeviceStatus.Active:
            raise ValueError("device is not active")
        return device

    async def device_icmp_reachable(self) -> bool:
        return True

    async def device_ssh_reachable(self) -> bool:
        return True

    async def device_snmpv2_reachable(self) -> bool:
        return True


device_service = DeviceService(Device)
