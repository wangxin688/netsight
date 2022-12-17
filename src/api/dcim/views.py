from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth.models import User
from src.api.base import BaseListResponse, BaseResponse, CommonQueryParams
from src.api.dcim import schemas
from src.api.dcim.models import (
    DeviceRole,
    DeviceType,
    Location,
    Manufacturer,
    Rack,
    RackRole,
    Region,
    Site,
)
from src.api.deps import get_current_user, get_session
from src.api.ipam.models import ASN
from src.api.netsight.models import Contact
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_0, ERR_NUM_4004, ERR_NUM_4009

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class RegionCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/regions")
    async def create_region(self, region: schemas.RegionCreate) -> BaseResponse[int]:
        new_region = Region(**region.dict(exclude_none=True))
        self.session.add(new_region)
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            return {
                "code": ERR_NUM_4009.code,
                "data": None,
                "msg": f"Region with name: `{region.name}` already exists in the same level",
            }
        await self.session.flush()
        return_info = ERR_NUM_0
        return_info.data = new_region.id
        return return_info.dict()

    @router.get("/regions/{id}")
    async def get_region(self, id: int) -> BaseResponse[schemas.Region]:
        local_region = await self.session.get(Region, id)
        if local_region is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Region #{id} not found"
            return return_info.dict()
        return_info = ERR_NUM_0
        return_info.data = local_region
        return return_info.dict()

    @router.get("/regions")
    async def get_regions(
        self,
        region: schemas.RegionQuery = Depends(),
        common_params: CommonQueryParams = Depends(CommonQueryParams),
    ) -> BaseListResponse[List[schemas.Region]]:
        stmt = select(Region)
        count_stmt = select(func.count(Region.id))
        if not common_params.q:
            if region is not None:
                if region.id:
                    stmt = stmt.where(Region.id.in_(region.id))
                    count_stmt = count_stmt.where(Region.id.in_(region.id))
                if region.name:
                    stmt = stmt.where(Region.name == region.name)
                    count_stmt = count_stmt.where(Region.name == region.name)
        else:
            stmt = stmt.where(Region.name.ilike(f"%{common_params.q}%"))
            count_stmt = count_stmt.where(Region.name.ilike(f"%{common_params.q}%"))
        stmt = stmt.slice(
            common_params.offset, common_params.offset + common_params.limit
        )
        results = (await self.session.execute(stmt)).scalars().all()
        count = (await self.session.execute(count_stmt)).scalar()
        return_info = ERR_NUM_0
        return_info.data = {"count": count, "results": results}
        return return_info.dict()

    @router.put("/regions/{id}")
    async def update_region(
        self, id: int, region: schemas.RegionUpdate
    ) -> BaseResponse[int]:
        local_region: Region | None = await self.session.get(Region, id)
        if not local_region:
            return_info = ERR_NUM_4004
            return_info.data = local_region
            return return_info.dict()
        stmt = (
            update(Region)
            .where(Region.id == id)
            .values(**region.dict(exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            return {
                "code": ERR_NUM_4009.code,
                "data": None,
                "msg": f"Region with name '{region.name}' already exists in the same level",
            }
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info.dict()

    @router.put("/regions")
    async def bulk_update_regions(
        self, region: schemas.RegionBulkUpdate
    ) -> BaseResponse[List[int]]:
        local_regions = (
            (
                await self.session.execute(
                    select(Region.id).where(Region.id.in_(region.ids))
                )
            )
            .scalars()
            .all()
        )
        diff_region: set = set(region.ids) - set(local_regions)
        if diff_region:
            return_info = ERR_NUM_4004
            return_info.msg = f"Region #{list(diff_region)} not found"
            return return_info.dict()
        await self.session.execute(
            update(Region)
            .where(Region.id.in_(region.region_ids))
            .values(region.dict(exclude={"ids"}, exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = region.region_ids
        return return_info

    @router.delete("/regions/{id}")
    async def delete_region(self, id: int) -> BaseResponse[int]:
        local_region: Region | None = await self.session.get(Region, id)
        if local_region is None:
            return {
                "code": ERR_NUM_4004.code,
                "data": None,
                "msg": f"Region #{id} not found",
            }
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("/regions")
    async def bulk_delete_regions(
        self, region: schemas.RegionBulkDelete
    ) -> BaseResponse[List[int]]:
        regions: List[Region] = (
            (
                await self.session.execute(
                    select(Region).where(Region.id.in_(region.ids))
                )
            )
            .scalars()
            .all()
        )
        if len(regions) > 0:
            for _region in regions:
                await self.session.delete(_region)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = region.ids
        return return_info


@cbv(router)
class SiteCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/sites")
    async def create_site(
        self, site: schemas.SiteCreate
    ) -> BaseListResponse[List[schemas.Region]]:
        try:
            new_site = Site(**site.dict(exclude={"contact_ids"}))
            await self.session.add(new_site)
            await self.session.flush()
            if site.contact_ids:
                contacts: List[Contact] = (
                    (
                        await self.session.execute(
                            select(Contact).where(Contact.id.in_(site.contact_ids))
                        )
                    )
                    .scalars()
                    .all()
                )
                if len(contacts) > 0:
                    for contact in contacts:
                        new_site.contact.append(contact)
        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            return {
                "code": ERR_NUM_4009.code,
                "data": None,
                "msg": f"Site with `{site.name}` or `{site.site_code}` already exists",
            }
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = new_site.id
        return return_info

    @router.get("/sites/{id}")
    async def get_site(
        self,
        id: int,
    ) -> BaseResponse[schemas.Site]:
        result: AsyncResult = await self.session.execute(
            select(Site)
            .where(Site.id == id)
            .options(
                selectinload(
                    Site.dcim_device,
                    Site.dcim_location,
                    Site.dcim_rack,
                    Site.circuit_termination,
                )
            )
        )
        local_site: Site | None = result.scalars().first()
        if not local_site:
            return_info = ERR_NUM_4004
            return_info.msg = f"Site #{id} not found,  requested data not existed"
            return return_info
        return_info = ERR_NUM_0
        return_info.data = local_site
        return return_info

    @router.get("/sites")
    async def get_sites(self, site: schemas.SiteQuery):
        pass

    @router.put("/sites/{id}")
    async def update_site(
        self,
        id: int,
        site: schemas.SiteUpdate,
    ) -> BaseResponse[int]:
        local_site: Site | None = (
            (
                await self.session.execute(select(Site).where(Site.id == id)).options(
                    selectinload(Site.ipam_asn, Site.contact)
                )
            )
            .scalars()
            .first()
        )
        if not local_site:
            return {
                "code": ERR_NUM_4004.code,
                "data": None,
                "msg": f"Site #{id} not found",
            }
        if site.ipam_asn_ids:
            asns: List[ASN] | None = local_site.ipam_asn
            asn_ids = [asn.id for asn in asns]
            for asn in asns:
                if asn.id not in site.ipam_asn_ids:
                    local_site.ipam_asn.remove(asn)
            for ipam_asn_id in site.ipam_asn_ids:
                if ipam_asn_id not in asn_ids:
                    _asn: ASN | None = (
                        (
                            await self.session.execute(
                                select(ASN).where(ASN.id == ipam_asn_id)
                            )
                        )
                        .scalars()
                        .one_or_none()
                    )
                if _asn:
                    local_site.ipam_asn.append(_asn)

        if site.contact_ids:
            contacts: List[Contact] | None = local_site.contact
            contact_ids = [contact.id for contact in contacts]
            for contact in contacts:
                if contact.id not in site.contact_ids:
                    local_site.contact.remove(contact)
            for contact_id in site.contact_ids:
                if contact_id not in contact_ids:
                    _contact: Contact = (
                        (
                            await self.session.execute(
                                select(Contact).where(Contact.id == contact_id)
                            )
                        )
                        .scalars()
                        .one_or_none()
                    )
                    if _contact:
                        local_site.contact.append(contact)
        update_data = site.dict(exclude={"ipam_asn_ids", "contact_ids"})
        if update_data:
            try:
                await self.session.execute(
                    update(Site)
                    .where(Site.id == id)
                    .values(**update_data)
                    .execute_options(synchronize_session="fetch")
                )
            except IntegrityError as e:
                logger.error(e)
                await self.session.rollback()
                return_info = ERR_NUM_4009
                return_info.msg = f"Site with name `{site.name}` or site_code `{site.site_code}` already exists"
                return return_info.dict()
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.put("/sites")
    async def bulk_update_sites(
        self, site: schemas.SiteBulkUpdate
    ) -> BaseResponse[List[int]]:
        pass

    @router.delete("/sites/{id}")
    async def delete_site(
        self,
        id: int,
    ) -> BaseResponse[int]:
        local_site: Site | None = await self.session.get(Site, id)
        if not local_site:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete site failed, site #{id} not found"
            return return_info
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("/sites")
    async def bulk_delete_sites(
        self, site: schemas.SiteBulkDelete
    ) -> BaseResponse[List[int]]:
        local_sites: List[Site] | None = (
            (await self.session.execute(select(Site).where(Site.id.in_(site.ids))))
            .scalars()
            .all()
        )
        if local_sites is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete sites failed, sites #{id} not found"
            return return_info
        return_info = ERR_NUM_0
        return_info.data = site.ids
        return return_info


@cbv(router)
class LocationCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/locations")
    async def create_location(
        self, location: schemas.LocationCreate
    ) -> BaseResponse[int]:
        site: Site | None = (
            (
                await self.session.execute(
                    select(Site).where(Site.id == location.site_id)
                )
            )
            .scalars()
            .first()
        )
        if not site:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Create Location failed, Site #{location.site_id} not found"
            )
            return return_info
        try:
            new_location = Location(**location.dict(exclude_none=True))
            await self.session.add(new_location)
            await self.session.commit()
            await self.session.flush()
            return_info = ERR_NUM_0
            return_info.data = new_location.id
            return return_info
        except SQLAlchemyError as e:
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = f"Create Location failed, Location with same name `{location.name}` already exists"
            return return_info

    @router.get("/locations/{id}")
    async def get_location(self, id: int) -> BaseResponse[schemas.Location]:
        local_location: Location | None = await self.session.get(Location, id)
        if not local_location:
            return_info = ERR_NUM_4004
            return_info.msg = f"Location #{id} not found"
            return return_info.dict()
        return_info = ERR_NUM_0
        return_info.data = local_location
        return return_info.dict()

    @router.get("/locations")
    async def get_locations(
        self, location: schemas.LocationQuery
    ) -> BaseListResponse[List[schemas.Location]]:
        pass

    @router.put("/locations/{id}")
    async def update_location(
        self, id: int, location: schemas.LocationUpdate
    ) -> BaseResponse[int]:
        local_location: Location | None = (
            (await self.session.execute(select(Location).where(Location.id == id)))
            .scalars()
            .first()
        )
        if not local_location:
            return_info = ERR_NUM_4009
            return_info.msg = f"Update location failed, location #{id} not found"
            return return_info
        if local_location.site_id:
            local_site = (
                (
                    await self.session.execute(
                        select(Site).where(Site.id == local_location.site_id)
                    )
                )
                .scalars()
                .first()
            )
            if not local_site:
                return_info = ERR_NUM_4009
                return_info.msg = f"Update location failed, site #{id} not found"
                return return_info
        await self.session.execute(
            update(Location)
            .where(Location.id == id)
            .values(**location(exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("/locations/{id}")
    async def delete_location(self, id: int) -> BaseResponse[int]:
        local_location: Location | None = (
            (await self.session.execute(select(Location).where(Location.id == id)))
            .scalars()
            .first()
        )
        if not local_location:
            return_info = ERR_NUM_4009
            return_info.msg = f"Update location failed, location #{id} not found"
            return return_info
        await self.session.delete(local_location)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info


@cbv(router)
class RackRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/rack-roles")
    async def create_rack_role(self, rack: schemas.RackRoleCreate) -> BaseResponse[int]:
        local_rack_role: RackRole | None = (
            (
                await self.session.execute(
                    select(RackRole).where(RackRole.name == rack.name)
                )
            )
            .scalars()
            .first()
        )
        if local_rack_role is not None:
            return_info = ERR_NUM_4009
            return_info.msg = f"Rack role with name {rack.name} already exists"
            return return_info.dict()
        new_rack_role = RackRole(**rack.dict())
        await self.session.add(new_rack_role)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = new_rack_role.id
        return return_info.dict()

    @router.get("/rack-roles/{id}")
    async def get_rack_role(self, id: int) -> BaseResponse[schemas.RackRole]:
        local_rack_role: RackRole | None = (
            (await self.session.execute(select(RackRole).where(RackRole.id == id)))
            .scalars()
            .first()
        )
        if not local_rack_role:
            return_info = ERR_NUM_4004
            return_info.msg = f"Rack role #{id} not found"
            return return_info
        return_info = ERR_NUM_0
        return_info.data = local_rack_role
        return return_info

    @router.get("/rack-roles")
    async def get_rack_roles(
        self, rack_role: schemas.RackRoleQuery
    ) -> BaseListResponse[List[schemas.RackRole]]:
        pass

    @router.put("/rack-roles/{id}")
    async def update_rack_role(
        self, id: int, rack_role: schemas.RackRoleUpdate
    ) -> BaseResponse[int]:
        local_rack_role: RackRole | None = (
            (await self.session.execute(select(RackRole).where(RackRole.id == id)))
            .scalars()
            .first()
        )
        if not local_rack_role:
            return_info = ERR_NUM_4004
            return_info.msg = f"Rack role #{id} not found"
            return return_info
        await self.session.update(RackRole).where(RackRole.id == id).values(
            **rack_role.dict(exclude_none=True)
        ).execute_options(synchronize_session="fetch")
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("/rack-roles/{id}")
    async def delete_rack_role(self, id: int) -> BaseResponse[int]:
        local_rack_role: RackRole | None = (
            (await self.session.execute(select(RackRole).where(RackRole.id == id)))
            .scalars()
            .first()
        )
        if local_rack_role is None:
            return {
                "code": ERR_NUM_4004.code,
                "data": None,
                "msg": f"Rack role #{id} not found",
            }
        await self.session.delete(local_rack_role)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("rack-roles")
    async def delete_rack_roles(self, rack_role: schemas.RackRoleBulkDelete):
        rack_roles: List[RackRole] = (
            (
                await self.session.execute(
                    select(RackRole).where(RackRole.id.in_(rack_role.ids))
                )
            )
            .scalars()
            .all()
        )
        if len(rack_roles) > 0:
            for _rack_role in rack_roles:
                await self.session.delete(_rack_role)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = rack_role.ids
        return return_info


@cbv(router)
class RackCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/racks")
    async def create_rack(self, rack: schemas.RackCreate) -> BaseResponse[int]:
        local_rack: Rack | None = (
            (await self.session.execute(select(Rack).where(Rack.name == rack.name)))
            .scalars()
            .first()
        )
        local_site: Site | None = (
            (await self.session.execute(select(Site.id).where(Site.id == rack.site_id)))
            .scalars()
            .first()
        )
        # local_location: Location | None = ()
        if local_rack is not None:
            return_info = ERR_NUM_4009
            return_info.msg = f"Rack with name `{rack.name}` already exists"
            return return_info
        if local_site is None:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Create rack failed, rack with site #{rack.site_id} not found"
            )
            return return_info
        # new_rack = Rack(**rack.dict(exclude={"location_id", "device_ids", ""}))

    @router.get("/racks/{id}")
    async def get_rack(self, id: int) -> BaseResponse[schemas.Rack]:
        pass

    @router.get("/racks")
    async def get_racks(
        self, rack: schemas.RackQuery
    ) -> BaseListResponse[List[schemas.Rack]]:
        pass

    @router.put("/racks/{id}")
    async def update_rack(self, rack: schemas.RackUpdate) -> BaseResponse[int]:
        pass

    @router.delete("/racks/{id}")
    async def delete_rack(self, id: int) -> BaseResponse[int]:
        pass


@cbv(router)
class ManufacturerCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/manufacturers")
    async def create_manufacturer(
        self, manufacturer: schemas.ManufacturerCreate
    ) -> BaseResponse[int]:
        local_manufacturer: Manufacturer | None = (
            (
                await self.session.execute(
                    select(Manufacturer).where(Manufacturer.name == manufacturer.name)
                )
            )
            .scalars()
            .first()
        )
        if local_manufacturer is not None:
            return {
                "code": ERR_NUM_4009.code,
                "data": None,
                "msg": f"Manufacturer with name {manufacturer.name} already exists",
            }
        new_manufacturer = Manufacturer(
            **manufacturer.dict(exclude={"device_type_ids"})
        )
        await self.session.add(new_manufacturer)
        if manufacturer.device_type_ids:
            device_types: List[DeviceType] | None = (
                (
                    await self.session.execute(
                        select(DeviceType).where(
                            DeviceType.id.in_(manufacturer.device_type_ids)
                        )
                    )
                )
                .scalar()
                .all()
            )
            if len(device_types) > 0:
                for device_type in device_types:
                    if device_type.manufacturer_id != new_manufacturer.id:
                        device_type.manufacturer_id = new_manufacturer.id
                        await self.session.add(device_type)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = new_manufacturer.id
        return return_info.dict()

    @router.get("/manufacturers/{id}")
    async def get_manufacturer(self, id: int) -> BaseResponse[schemas.Manufacturer]:
        local_manufacturer: Manufacturer | None = (
            (
                await self.session.execute(
                    select(Manufacturer).where(Manufacturer.id == id)
                )
            )
            .scalars()
            .first()
        )
        if not local_manufacturer:
            return_info = ERR_NUM_4004
            return_info.msg = f"Manufacturer #{id} not found"
        return_info = ERR_NUM_0
        return_info.data = local_manufacturer
        return return_info.dict()

    @router.get("/manufacturers")
    async def get_manufacturers(
        self, manufacturer: schemas.ManufacturerQuery
    ) -> BaseListResponse[List[schemas.Manufacturer]]:
        pass

    @router.put("/manufacturers/{id}")
    async def update_manufacturer(
        self, id: int, manufacturer: schemas.ManufacturerUpdate
    ) -> BaseResponse[int]:
        local_manufacturer: Manufacturer | None = (
            (
                await self.session.execute(
                    select(Manufacturer).where(Manufacturer.id == id)
                )
            )
            .scalars()
            .first()
        )
        if not local_manufacturer:
            return {
                "code": ERR_NUM_4004.code,
                "data": None,
                "msg": "Manufacturer #id not found",
            }
        await self.session.execute(
            update(Manufacturer)
            .where(manufacturer.id == id)
            .values(**manufacturer.dict(exclude={"device_type_ids"}))
            .execute_options(synchronize_session="fetch")
        )
        if manufacturer.device_type_ids is not None:
            device_types: List[DeviceType] | None = (
                (
                    await self.session.execute(
                        select(DeviceType).where(
                            DeviceType.id.in_(manufacturer.device_type_ids)
                        )
                    )
                )
                .scalar()
                .all()
            )
            if len(device_types) > 0:
                for device_type in device_types:
                    if device_type.manufacturer_id != id:
                        device_type.manufacturer_id = id
                        await self.session.add(device_type)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("/manufacturers/{id}")
    async def delete_manufacturer(self, id: int) -> BaseResponse[int]:
        local_manufacturer: Manufacturer | None = (
            (
                await self.session.execute(
                    select(Manufacturer).where(Manufacturer.id == id)
                )
            )
            .scalars()
            .first()
        )
        if not local_manufacturer:
            return_info = ERR_NUM_4004
            return_info.msg = f"Manufacturer #{id} not found"
            return return_info
        await self.session.delete(local_manufacturer)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info


@cbv(router)
class DeviceTypeCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/device-types")
    async def create_device_type(
        self, device_type: schemas.DeviceTypeCreate
    ) -> BaseResponse[int]:
        local_deive_type: DeviceType | None = (
            await self.session.execute(
                select(DeviceType).where(DeviceType.name == device_type.name)
            )
            .scalars()
            .first()
        )
        if local_deive_type is not None:
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Device Type with name `{device_type.name}` already existed"
            )
            return return_info
        if device_type.manufacturer_id is not None:
            manufacture: Manufacturer | None = (
                await self.session.execute(
                    select(Manufacturer).where(
                        Manufacturer.id == device_type.manufacturer_id
                    )
                )
                .scalars()
                .all()
            )
            if not manufacture:
                return_info = ERR_NUM_4004
                return_info.msg = f"Manufacturer #{id} not found"
                return return_info
        new_device_type = DeviceType(**device_type.dict(exclude_none=True))
        await self.session.add(new_device_type)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = new_device_type.id
        return return_info.dict()

    @router.get("/device-types/{id}")
    async def get_device_type(self, id: int) -> BaseResponse[schemas.DeviceType]:
        local_device_type = await self.session.get(DeviceType, id)
        if not local_device_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device type #{id} not found"
            return return_info.dict()
        return_info = ERR_NUM_0
        return_info.data = local_device_type
        return return_info.dict()

    @router.get("/device-types")
    async def get_device_types(
        self, device_type: schemas.DeviceTypeQuery
    ) -> BaseListResponse[List[schemas.DeviceType]]:
        pass

    @router.put("/device-types/{id}")
    async def update_device_type(
        self, device_type: schemas.DeviceTypeUpdate
    ) -> BaseResponse[int]:
        local_deive_type: DeviceType | None = (
            await self.session.execute(select(DeviceType).where(DeviceType.id == id))
            .scalars()
            .first()
        )
        if not local_deive_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device Type #{id} not found"
            return return_info.dict()
        if device_type.manufacturer_id:
            manufacture: Manufacturer | None = (
                await self.session.execute(
                    select(Manufacturer).where(
                        Manufacturer.id == device_type.manufacturer_id
                    )
                )
                .scalars()
                .all()
            )
            if not manufacture:
                return_info = ERR_NUM_4004
                return_info.msg = f"Manufacturer #{id} not found"
                return return_info.dict()
        await self.session.execute(
            update(DeviceType)
            .where(DeviceType.id == id)
            .values(**device_type.dict(exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info.dict()

    @router.delete("/device-types/{id}")
    async def delete_device_type(self, id: int) -> BaseResponse[int]:
        local_deive_type: DeviceType | None = (
            await self.session.execute(select(DeviceType).where(DeviceType.id == id))
            .scalars()
            .first()
        )
        if not local_deive_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device Type #{id} not found"
            return return_info.dict()

        await self.session.delete(local_deive_type)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info.dict()


@cbv(router)
class DeviceRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/device-roles")
    async def create_device_role(
        self, device_role: schemas.DeviceRoleCreate
    ) -> BaseResponse[int]:
        local_device_role: DeviceRole | None = (
            (
                await self.session.execute(
                    select(DeviceRole).where(DeviceRole.name == device_role.name)
                )
            )
            .scalars()
            .first()
        )
        if local_device_role is not None:
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Device role with name: `{device_role.name}` already exsits"
            )
            return return_info.dict()
        new_device_role = DeviceRole(**device_role.dict(exclude_none=True))
        await self.session.add(new_device_role)
        await self.session.commit(new_device_role)
        return_info = ERR_NUM_0
        return_info.data = new_device_role.id
        return return_info.dict()

    @router.get("/device-roles/{id}")
    async def get_device_role(self, id: int) -> BaseResponse[schemas.DeviceRole]:
        pass

    @router.get("/device-roles")
    async def get_device_roles(
        self, device_role: schemas.DeviceRoleQuery
    ) -> BaseListResponse[List[schemas.DeviceRole]]:
        pass

    @router.put("/device-roles/{id}")
    async def update_device_role(
        self, device_role: schemas.DeviceRoleUpdate
    ) -> BaseResponse[int]:
        local_device_role: DeviceRole | None = (
            (await self.session.execute(select(DeviceRole).where(DeviceRole.id == id)))
            .scalars()
            .first()
        )
        if local_device_role is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device role #{id} not found"
            return return_info.dict()
        try:
            await self.session.execute(
                update(DeviceRole)
                .where(DeviceRole.id == id)
                .values(**device_role.dict(exclude_none=True))
                .execute_options(synchronize_session="fetch")
            )
            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Device Role with name `{device_role.name}` already exists"
            )
            return return_info.dict()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info

    @router.delete("/device-roles/{id}")
    async def delete_device_role(self, id: int) -> BaseResponse[int]:
        local_device_role: DeviceRole | None = (
            (await self.session.execute(select(DeviceRole).where(DeviceRole.id == id)))
            .scalars()
            .first()
        )
        if local_device_role is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device role #{id} not found"
            return return_info.dict()
        await self.session.delete(local_device_role)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = id
        return return_info.dict()


@cbv(router)
class InterfaceCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/interfaces")
    async def create_interface(
        self, interface: schemas.InterfaceCreate
    ) -> BaseResponse[int]:
        pass

    @router.get("/interfaces/{id}")
    async def get_interface(self, id: int) -> BaseResponse[int]:
        pass

    @router.get("/interfaces/")
    async def get_interfaces(
        self, interface: schemas.InterfaceQuery
    ) -> BaseListResponse[List[schemas.Interface]]:
        pass

    @router.put("/interfaces/{id}")
    async def update_interface(
        self, interface: schemas.InterfaceUpdate
    ) -> BaseResponse[int]:
        pass
