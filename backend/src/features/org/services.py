from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import or_, select, update

from src.core.repositories import BaseRepository
from src.core.utils.context import locale_ctx
from src.features.circuit.models import Circuit
from src.features.consts import CircuitStatus, DeviceStatus, PrefixStatus, SiteStatus, VLANStatus
from src.features.dcim.models import Device
from src.features.ipam.models import VLAN, Prefix
from src.features.org import schemas
from src.features.org.models import Location, Site, SiteGroup
from src.libs.countries import get_country_by_name

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("site_group_service", "site_service", "location_service")


class SiteGroupService(
    BaseRepository[SiteGroup, schemas.SiteGroupCreate, schemas.SiteGroupUpdate, schemas.SiteGroupQuery]
): ...


class SiteService(BaseRepository[Site, schemas.SiteCreate, schemas.SiteUpdate, schemas.SiteQuery]):
    def get_country_info(self, country: str) -> tuple[str, int | None]:
        country_info = get_country_by_name(country, locale_ctx.get())
        if country_info:
            country_name = country_info["visible_name"]
            time_zone = country_info["timezone"]
            return country_name, time_zone
        return country, None

    async def create(
        self,
        session: "AsyncSession",
        obj_in: schemas.SiteCreate,
        excludes: set[str] | None = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        commit: bool | None = False,
    ) -> Site:
        country_name, timezone = None, None
        if obj_in.country:
            country_name, timeozne = self.get_country_info(obj_in.country)
        new_site = await super().create(session, obj_in, excludes, exclude_unset, exclude_none, commit)
        new_site.country = country_name
        new_site.time_zone = timezone
        session.add(new_site)
        await session.commit()
        await session.refresh(new_site)
        return new_site

    async def update(
        self,
        session: "AsyncSession",
        db_obj: Site,
        obj_in: schemas.SiteUpdate,
        excludes: set[str] | None = None,
        commit: bool | None = True,
    ) -> Site:
        if obj_in.country and obj_in.country != db_obj.country:
            country_name, timeozne = self.get_country_info(obj_in.country)
            db_obj.country = country_name
            db_obj.time_zone = timeozne
        if obj_in.status and obj_in.status == SiteStatus.Retired and db_obj.status != obj_in.status:
            await session.execute(
                update(Device).where(Device.site_id == db_obj.id).values(status=DeviceStatus.Offline.value)
            )
            await session.execute(
                update(Circuit)
                .where(or_(Circuit.site_a_id == db_obj.id, Circuit.site_z_id == db_obj.id))
                .values(status=CircuitStatus.Offline.value)
            )
            await session.execute(
                update(VLAN).where(VLAN.site_id == db_obj.id).values(status=VLANStatus.Deprecated.value)
            )
            await session.execute(
                update(Prefix).where(Prefix.site_id == db_obj.id).values(status=PrefixStatus.Deprecated.value)
            )
        return await super().update(session, db_obj, obj_in, excludes, commit)

    async def get_site_locations(self, session: "AsyncSession", site_id: int) -> Sequence[Location]:
        location_service = LocationService(Location)
        stmt = location_service._get_base_stmt().where(Location.site_id == site_id)  # noqa: SLF001
        return (await session.scalars(stmt)).all()


class LocationService(BaseRepository[Location, schemas.LocationCreate, schemas.LocationUpdate, schemas.LocationQuery]):
    async def get_location_site_id(self, session: "AsyncSession", location_id: int) -> int:
        return (await session.scalars(select(Location.site_id).where(Location.id == location_id))).one()


site_group_service = SiteGroupService(SiteGroup)
site_service = SiteService(Site)
location_service = LocationService(Location)
