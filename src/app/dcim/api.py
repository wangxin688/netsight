from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.app.auth.models import User
from src.app.base import BaseListResponse, BaseResponse, QueryParams
from src.app.dcim import schemas
from src.app.dcim.models import (
    DeviceRole,
    DeviceType,
    Interface,
    Location,
    Manufacturer,
    Platform,
    Rack,
    RackRole,
    Region,
    Site,
)
from src.app.deps import get_current_user, get_locale, get_session
from src.app.ipam.models import ASN
from src.app.netsight.models import Contact
from src.db.crud_base import CRUDBase
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_404, ERR_NUM_409, ResponseMsg, error_404_409

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class RegionCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Region)
    locale = Depends(get_locale)

    @router.post("/regions")
    async def create_region(self, region: schemas.RegionCreate) -> BaseResponse[int]:
        """create a new region"""
        if region.parent_id:
            local_region = self.session.get(Region, region.parent_id)
            if not local_region:
                return_info = error_404_409(
                    ERR_NUM_404, self.locale, "region", "parent_id", id
                )
                return return_info
        new_region = Region(**region.dict(exclude_none=True))
        self.session.add(new_region)
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "region", "name", region.name
            )
            return return_info
        await self.session.flush()
        return_info = ResponseMsg(data=new_region.id, locale=self.locale)
        return return_info

    @router.get("/regions/{id}")
    async def get_region(self, id: int) -> BaseResponse[schemas.Region]:
        """get a region"""
        local_region = await self.session.get(Region, id)
        if local_region is None:
            return_info = error_404_409(ERR_NUM_404, self.locale, "region", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_region, locale=self.locale)
        return return_info

    @router.get("/regions")
    async def get_regions(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.RegionBase]]:
        """get regions without custom parameters"""
        local_regions = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": local_regions}, locale=self.locale
        )
        return return_info

    @router.post("/regions/getList")
    async def get_regions_filter(
        self,
        region: schemas.RegionQuery,
    ) -> BaseListResponse[List[schemas.Region]]:
        """get regions with custom parameters"""
        stmt = select(Region)
        count_stmt = select(func.count(Region.id))
        if region is not None:
            if region.id:
                stmt = stmt.where(Region.id.in_(region.id))
                count_stmt = count_stmt.where(Region.id.in_(region.id))
            if region.name:
                stmt = stmt.where(Region.name == region.name)
                count_stmt = count_stmt.where(Region.name == region.name)
        if region.q:
            stmt = stmt.where(Region.name.ilike(f"%{region.q}%"))
            count_stmt = count_stmt.where(Region.name.ilike(f"%{region.q}%"))
        stmt = stmt.slice(region.offset, region.offset + region.limit)
        results = (await self.session.execute(stmt)).scalars().all()
        count = (await self.session.execute(count_stmt)).scalar()
        return_info = ResponseMsg(
            data={"count": count, "results": results}, locale=self.locale
        )
        return return_info

    @router.put("/regions/{id}")
    async def update_region(
        self, id: int, region: schemas.RegionUpdate
    ) -> BaseResponse[int]:
        """update a region"""
        local_region: Region | None = await self.session.get(Region, id)
        if not local_region:
            return_info = error_404_409(ERR_NUM_404, self.locale, "region", "#id", "id")
            return return_info
        if region.parent_id:
            parent_region = self.session.get(Region, region.parent_id)
            if not parent_region:
                return_info = error_404_409(
                    ERR_NUM_404, self.locale, "region", "parent_id", "id"
                )
            return return_info
        try:
            await self.crud.update(self.session, id, region)
        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "region", "name in same level", region.name
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/regions/updateList")
    async def bulk_update_regions(
        self, region: schemas.RegionBulkUpdate
    ) -> BaseResponse[List[int]]:
        """bulk update a list of regions"""
        local_regions = await self.crud.get_multi(self.session, region.ids)
        diff_region: set = set(region.ids) - set(
            [region.id for region in local_regions]
        )
        if diff_region:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "region", "#ids", diff_region
            )
            return return_info
        await self.crud.update_multi(self.session, region.ids, region, excludes={"ids"})
        return_info = ResponseMsg(data=region.ids, locale=self.locale)
        return return_info

    @router.delete("/regions/{id}")
    async def delete_region(self, id: int) -> BaseResponse[int]:
        """delete a region"""
        local_region: Region | None = await self.crud.delete(self.session, id)
        if local_region is None:
            return_info = error_404_409(ERR_NUM_404, self.locale, "region", "#id", "id")
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/regions/deleteList")
    async def bulk_delete_regions(
        self, region: schemas.RegionBulkDelete
    ) -> BaseResponse[List[int]]:
        """bulk delete regions"""
        local_regions = await self.crud.delete_multi(self.session, region.ids)
        if not local_regions:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "region", "#ids", region.ids
            )
            return return_info
        return_info = ResponseMsg(
            data=[d.id for d in local_regions], locale=self.locale
        )
        return return_info


@cbv(router)
class SiteCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Site)
    locale = Depends(get_locale)

    @router.post("/sites")
    async def create_site(
        self, site: schemas.SiteCreate
    ) -> BaseListResponse[List[schemas.Region]]:
        """Create a new site"""
        contact_crud = CRUDBase(Contact)
        new_site = Site(**site.dict(exclude={"contact_ids"}))
        exist_name = await self.crud.get_by_field(self.session, "name", site.name)
        if exist_name:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "site", "name", site.name
            )
            return return_info
        exist_code = await self.crud.get_by_field(
            self.session, "site_code", site.site_code
        )
        if exist_code:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "site", "site_code", site.site_code
            )
            return return_info
        await self.session.add(new_site)
        await self.session.flush()
        if site.contact_ids:
            contacts: List[Contact] = await contact_crud.get_multi(
                self.session, site.contact_ids
            )
            if len(contacts) > 0:
                for contact in contacts:
                    new_site.contact.append(contact)
            else:
                return_info = error_404_409(
                    ERR_NUM_404, self.locale, "contact", "#ids", site.contact_ids
                )
                return return_info
        await self.session.commit()
        return_info = ResponseMsg(data=new_site.id)
        return return_info

    @router.get("/sites/{id}")
    async def get_site(
        self,
        id: int,
    ) -> BaseResponse[schemas.Site]:
        """Get the site"""
        local_site: AsyncResult = await self.crud.get(
            Site,
            id,
            options=(
                selectinload(
                    Site.dcim_device,
                    Site.dcim_location,
                    Site.dcim_rack,
                    Site.circuit_termination,
                ),
            ),
        )
        if not local_site:
            return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_site)
        return return_info

    @router.get("/sites")
    async def get_sites(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.SiteBase]]:
        """get sites without custom parameters"""
        local_sites: List[Site] = await self.crud.get_all(
            self.session, q.limit, q.offset
        )
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": local_sites}, locale=self.locale
        )
        return return_info

    @router.post("/sites/getList")
    async def get_sites_filter(
        self, site: schemas.SiteQuery
    ) -> BaseListResponse[List[schemas.SiteBase]]:
        """get sites with custom parameters"""

    @router.put("/sites/{id}")
    async def update_site(
        self,
        id: int,
        site: schemas.SiteUpdate,
    ) -> BaseResponse[int]:
        local_site: Site | None = await self.session.get(
            Site, id, options=(selectinload(Site.ipam_asn, Site.contact),)
        )
        if not local_site:
            return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        if site.ipam_asn_ids:
            asns: List[ASN] | None = local_site.ipam_asn
            asn_ids = [asn.id for asn in asns]
            for asn in asns:
                if asn.id not in site.ipam_asn_ids:
                    local_site.ipam_asn.remove(asn)
            for ipam_asn_id in site.ipam_asn_ids:
                if ipam_asn_id not in asn_ids:
                    _asn: ASN | None = await self.session.get(ASN, ipam_asn_id)
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
                    _contact: Contact | None = await self.session.get(
                        Contact, contact_id
                    )
                    if _contact:
                        local_site.contact.append(contact)
        exist_name = await self.crud.get_by_field(self.session, "name", site.name)
        if exist_name:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "site", "name", site.name
            )
            return return_info
        exist_code = await self.crud.get_by_field(
            self.session, "site_code", site.site_code
        )
        if exist_code:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "site", "site_code", site.site_code
            )
            return return_info
        await self.crud.update(
            self.session, id, site, excludes={"ipam_asn_ids", "contact_ids"}
        )
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/sites/updateList")
    async def bulk_update_sites(
        self, site: schemas.SiteBulkUpdate
    ) -> BaseResponse[List[int]]:
        pass

    @router.delete("/sites/{id}")
    async def delete_site(
        self,
        id: int,
    ) -> BaseResponse[int]:
        local_site: Site | None = await self.crud.delete(self.session, id)
        if not local_site:
            return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/sites/deleteList")
    async def bulk_delete_sites(
        self, site: schemas.SiteBulkDelete
    ) -> BaseResponse[List[int]]:
        """bulk delete sites"""
        local_sites: List[Site] = await self.crud.delete_multi(self.session, site.ids)
        if local_sites is None:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "site", "#ids", site.ids
            )
            return return_info
        return_info = ResponseMsg(data=[d.id for d in local_sites], locale=self.locale)
        return return_info


@cbv(router)
class LocationCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Location)
    locale = Depends(get_locale)

    @router.post("/locations")
    async def create_location(
        self, location: schemas.LocationCreate
    ) -> BaseResponse[int]:
        site: Site | None = await self.session.get(Site, location.site_id)
        if not site:
            return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        exsit_name = await self.crud.get_by_field(self.session, "name", location.name)
        if exsit_name:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "location", "name", location.name
            )
            return return_info
        new_location = Location(**location.dict(exclude_none=True))
        await self.session.add(new_location)
        await self.session.commit()
        return_info = ResponseMsg(data=new_location.id, locale=self.locale)
        return return_info

    @router.get("/locations/{id}")
    async def get_location(self, id: int) -> BaseResponse[schemas.Location]:
        local_location: Location | None = await self.session.get(Location, id)
        if not local_location:
            return_info = error_404_409(ERR_NUM_404, self.locale, "location", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_location, locale=self.locale)
        return return_info

    @router.get("/locations")
    async def get_locations(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.LocationBase]]:
        results: List[Location] = await self.crud.get_all(
            self.session, q.limit, q.offset
        )
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": results}, locale=self.locale
        )
        return return_info

    @router.post("/locations/getList")
    async def get_locations_filter(
        self, location: schemas.LocationQuery
    ) -> BaseListResponse[List[schemas.Location]]:
        pass

    @router.put("/locations/{id}")
    async def update_location(
        self, id: int, location: schemas.LocationUpdate
    ) -> BaseResponse[int]:
        local_location: Location | None = await self.session.get(Location, id)
        if not local_location:
            return_info = error_404_409(ERR_NUM_404, self.locale, "location", "#id", id)
            return return_info
        if local_location.site_id:
            local_site: Site | None = await self.session.get(
                Site, local_location.site_id
            )
            if not local_site:
                return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        if local_location.name:
            exist_name = await self.crud.get_by_field(
                self.session, "name", local_location.name
            )
            if exist_name:
                return_info = error_404_409(
                    ERR_NUM_409, self.locale, "location", "name", location.name
                )
                return return_info
        await self.crud.update(self.session, id, location)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/locations/{id}")
    async def delete_location(self, id: int) -> BaseResponse[int]:
        local_location: Location | None = await self.crud.delete(self.session, id)
        if not local_location:
            return_info = error_404_409(ERR_NUM_404, self.locale, "location", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/locations/deleteList")
    async def bulk_delete_locations(
        self, location: schemas.LocationBulkDelete
    ) -> BaseResponse[List[int]]:
        local_locations: List[Location] = await self.crud.delete_multi(
            self.session, location.ids
        )
        if not local_locations:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "location", "#ids", location.ids
            )
            return return_info
        return_info = ResponseMsg(
            data=[d.id for d in local_locations], locale=self.locale
        )
        return return_info


@cbv(router)
class RackRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(RackRole)
    locale = Depends(get_locale)

    @router.post("/rack-roles")
    async def create_rack_role(
        self, rack_role: schemas.RackRoleCreate
    ) -> BaseResponse[int]:
        local_rack_role: RackRole | None = await self.crud.get_by_field(
            self.session, "name", rack_role.name
        )
        if local_rack_role is not None:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "rack-role", "name", rack_role.name
            )
            return return_info
        new_rack_role = RackRole(**rack_role.dict())
        await self.session.add(new_rack_role)
        await self.session.commit()
        return_info = ResponseMsg(data=new_rack_role.id, locale=self.locale)
        return return_info

    @router.get("/rack-roles/{id}")
    async def get_rack_role(self, id: int) -> BaseResponse[schemas.RackRole]:
        local_rack_role: RackRole | None = await self.session.get(RackRole, id)
        if not local_rack_role:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "rack-role", "#id", id
            )
            return return_info
        return_info = ResponseMsg(data=local_rack_role, locale=self.locale)
        return return_info

    @router.get("/rack-roles")
    async def get_rack_roles(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.RackRoleBase]]:
        """get rack roles without custom parameters"""
        results: List[RackRole] = await self.crud.get_all(
            self.session, q.limit, q.offset
        )
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": results}, locale=self.locale
        )
        return return_info

    @router.post("/rack-roles/getList")
    async def get_rack_roles_filter(
        self, rack_role: schemas.RackRoleQuery
    ) -> BaseListResponse[List[schemas.RackRole]]:
        """get rack roles with custom parameters"""

    @router.put("/rack-roles/{id}")
    async def update_rack_role(
        self, id: int, rack_role: schemas.RackRoleUpdate
    ) -> BaseResponse[int]:
        local_rack_role: RackRole | None = await self.session.get(RackRole, id)
        if not local_rack_role:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "rack-role", "#id", id
            )
            return return_info
        if rack_role.name:
            exist_role = await self.crud.get_by_field(
                self.session, "name", rack_role.name
            )
            if exist_role:
                return_info = error_404_409(
                    ERR_NUM_409, self.locale, "rack-role", "name", rack_role.name
                )
            return return_info
        await self.crud.update(self.session, id, rack_role)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/rack-roles/{id}")
    async def delete_rack_role(self, id: int) -> BaseResponse[int]:
        local_rack_role: RackRole | None = await self.crud.delete(self.session, id)
        if local_rack_role is None:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "rack-role", "#id", id
            )
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("rack-roles/deleteList")
    async def bulk_delete_rack_roles(
        self, rack_role: schemas.RackRoleBulkDelete
    ) -> BaseResponse[List[int]]:
        rack_roles: List[RackRole] = await self.crud.delete_multi(
            self.session, rack_role.ids
        )
        if len(rack_roles) == 0:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "rack-role", "#ids", rack_role.ids
            )
            return return_info
        return_info = ResponseMsg(data=[d.id for d in rack_roles], locale=self.locale)
        return return_info


@cbv(router)
class RackCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Rack)

    @router.post("/racks")
    async def create_rack(self, rack: schemas.RackCreate) -> BaseResponse[int]:
        local_rack: Rack | None = await self.crud.get_by_field(
            self.session, "name", rack.name
        )
        local_site: Site | None = await self.session.get(Site, rack.site_id)
        if rack.location_id:
            local_location: Location = await self.session.get(
                Location, rack.location_id
            )
            if local_location is None:
                return_info = ERR_NUM_4004
                return_info.msg = f"Create rack failed, rack with location #{rack.location_id} not found"
                return return_info
        if local_rack is not None:
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Create rack failed, rack with name `{rack.name}` already exists"
            )
            return return_info
        if local_site is None:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Create rack failed, rack with site #{rack.site_id} not found"
            )
            return return_info
        new_rack = Rack(**rack.dict())
        await self.session.add(new_rack)
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.get("/racks/{id}")
    async def get_rack(self, id: int) -> BaseResponse[schemas.RackBase]:
        local_rack: Rack = await self.session.get(Rack, id)
        if not local_rack:
            return_info = ERR_NUM_4004
            return_info.msg = f"Rack #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_rack)
        return return_info

    @router.get("/racks")
    async def get_racks(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[schemas.RackBase]:
        """get rack without custom parameters"""
        results: List[Rack] = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(func.count(select(Rack.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/racks/getList")
    async def get_racks_filter(
        self, rack: schemas.RackQuery
    ) -> BaseListResponse[List[schemas.Rack]]:
        """get racks with custom parameters"""

    @router.put("/racks/{id}")
    async def update_rack(self, rack: schemas.RackUpdate) -> BaseResponse[int]:
        pass

    @router.delete("/racks/{id}")
    async def delete_rack(self, id: int) -> BaseResponse[int]:
        local_rack: Rack = self.crud.delete(self.session, id)
        if not local_rack:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete rack failed, rack with id #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/racks/deleteList")
    async def bulk_delete_racks(
        self, rack: schemas.RackBulkDelete
    ) -> BaseListResponse[List[int]]:
        racks: List[Rack] = await self.crud.delete_multi(self.session, rack.ids)

        if not racks:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk delete racks failed, racks #{rack.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[d.id for d in racks])
        return return_info


@cbv(router)
class ManufacturerCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Manufacturer)

    @router.post("/manufacturers")
    async def create_manufacturer(
        self, manufacturer: schemas.ManufacturerCreate
    ) -> BaseResponse[int]:
        local_manufacturer: Manufacturer | None = await self.crud.get_by_field(
            self.session, "name", manufacturer.name
        )
        if local_manufacturer is not None:
            return_info = ERR_NUM_4009
            return_info.msg = f"Create manufacturer failed, manufacturer with name {manufacturer.name} already exists"
            return return_info
        new_manufacturer = Manufacturer(
            **manufacturer.dict(exclude={"device_type_ids"})
        )
        await self.session.add(new_manufacturer)
        if manufacturer.device_type_ids:
            device_type_crud = CRUDBase(DeviceType)
            device_types: List[DeviceType] | None = await device_type_crud.get_multi(
                self.session, manufacturer.device_type_ids
            )
            if len(device_types) > 0:
                for device_type in device_types:
                    if device_type.manufacturer_id != new_manufacturer.id:
                        device_type.manufacturer_id = new_manufacturer.id
                        await self.session.add(device_type)
        await self.session.commit()
        return_info = ResponseMsg(data=new_manufacturer.id)
        return return_info

    @router.get("/manufacturers/{id}")
    async def get_manufacturer(self, id: int) -> BaseResponse[schemas.Manufacturer]:
        local_manufacturer: Manufacturer | None = await self.session.get(
            Manufacturer, id
        )
        if not local_manufacturer:
            return_info = ERR_NUM_4004
            return_info.msg = f"Manufacturer #{id} not found"
        return_info = ResponseMsg(data=local_manufacturer)
        return return_info

    @router.get("/manufacturers")
    async def get_manufacturers(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.ManufacturerBase]]:
        results: List[Manufacturer] = await self.crud.get_all(
            self.session, q.limit, q.offset
        )
        count: int = (await self.session.execute(func.count(Manufacturer.id))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/manufacturers/getList")
    async def get_manufacturers_filter(
        self, manufacturer: schemas.ManufacturerQuery
    ) -> BaseListResponse[List[schemas.Manufacturer]]:
        pass

    @router.put("/manufacturers/{id}")
    async def update_manufacturer(
        self, id: int, manufacturer: schemas.ManufacturerUpdate
    ) -> BaseResponse[int]:
        local_manufacturer: Manufacturer | None = await self.session.get(
            Manufacturer, id, options=(selectinload(Manufacturer.dcim_device_type))
        )
        if not local_manufacturer:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Updated manufacturer failed, manufacturer #{id} not found "
            )
            return return_info
        await self.session.execute(
            update(Manufacturer)
            .where(manufacturer.id == id)
            .values(**manufacturer.dict(exclude={"device_type_ids"}))
            .execute_options(synchronize_session="fetch")
        )
        if manufacturer.device_type_ids is not None:
            device_type_crud = CRUDBase(DeviceType)
            device_types: List[DeviceType] | None = await device_type_crud.get_multi(
                self.session, manufacturer.device_type_ids
            )
            if len(device_types) > 0:
                for device_type in device_types:
                    if device_type.manufacturer_id != id:
                        device_type.manufacturer_id = id
                        await self.session.add(device_type)
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/manufacturers/{id}")
    async def delete_manufacturer(self, id: int) -> BaseResponse[int]:
        local_manufacturer: Manufacturer | None = await self.crud.delete(
            self.session, id
        )
        if not local_manufacturer:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Delete manufacturer failed, manufacturer #{id} not found"
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/manufacturers/deleteList")
    async def delete_manufacturers(
        self, manufacturer: schemas.ManufacturerBulkDelete
    ) -> BaseListResponse[List[int]]:
        results: List[Manufacturer] = await self.crud.delete_multi(
            self.session, manufacturer.ids
        )
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Bulk delete manufacturer failed, manufacturer #{id} not found"
            )
            return return_info
        return_info = ResponseMsg(data=[d.id for d in results])
        return return_info


@cbv(router)
class DeviceTypeCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(DeviceType)

    @router.post("/device-types")
    async def create_device_type(
        self, device_type: schemas.DeviceTypeCreate
    ) -> BaseResponse[int]:
        local_device_type: DeviceType | None = await self.crud.get_by_field(
            self.session, "name", device_type.name
        )
        if local_device_type is not None:
            return_info = ERR_NUM_4009
            return_info.msg = f"Create device type failed, device Type with name `{device_type.name}` already existed"
            return return_info
        if device_type.manufacturer_id is not None:
            manufacture: Manufacturer | None = await self.session.get(
                Manufacturer, device_type.manufacturer_id
            )
            if not manufacture:
                return_info = ERR_NUM_4004
                return_info.msg = (
                    f"Create device type failed, manufacturer #{id} not found"
                )
                return return_info
        new_device_type = DeviceType(**device_type.dict(exclude_none=True))
        await self.session.add(new_device_type)
        await self.session.commit()
        return_info = ResponseMsg(data=new_device_type.id)
        return return_info

    @router.get("/device-types/{id}")
    async def get_device_type(self, id: int) -> BaseResponse[schemas.DeviceType]:
        local_device_type = await self.session.get(DeviceType, id)
        if not local_device_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device type #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_device_type)
        return return_info

    @router.get("/device-types")
    async def get_device_types(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.DeviceTypeBase]]:
        results: List[DeviceType] = await self.crud.get_all(
            self.session, q.limit, q.offset
        )
        count: int = await self.session.execute(
            select(func.count(DeviceType.id))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/device-types/getList")
    async def get_device_types_filter(
        self, device_type: schemas.DeviceTypeQuery
    ) -> BaseListResponse[List[schemas.DeviceType]]:
        pass

    @router.put("/device-types/{id}")
    async def update_device_type(
        self, device_type: schemas.DeviceTypeUpdate
    ) -> BaseResponse[int]:
        local_device_type = await self.session.get(DeviceType, id)
        if not local_device_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Update device type failed, device type #{id} not found"
            return return_info
        if device_type.manufacturer_id:
            manufacture: Manufacturer | None = await self.session.get(
                Manufacturer, device_type.manufacturer_id
            )
            if not manufacture:
                return_info = ERR_NUM_4004
                return_info.msg = (
                    f"Update device type failed, manufacturer #{id} not found"
                )
                return return_info
        await self.session.execute(
            update(DeviceType)
            .where(DeviceType.id == id)
            .values(**device_type.dict(exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/device-types/{id}")
    async def delete_device_type(self, id: int) -> BaseResponse[int]:
        local_device_type = await self.crud.delete(self.session, id)
        if not local_device_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete device type failed, device Type #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/device-types/deleteList")
    async def delete_device_types(
        self, device_type: schemas.DeviceRoleBulkDelete
    ) -> BaseListResponse[List[int]]:
        local_device_type = await self.crud.delete(self.session, device_type.ids)
        if not local_device_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk delete device type failed, device Type #{device_type.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[d.id for d in local_device_type])
        return return_info


@cbv(router)
class DeviceRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(DeviceRole)

    @router.post("/device-roles")
    async def create_device_role(
        self, device_role: schemas.DeviceRoleCreate
    ) -> BaseResponse[int]:
        local_device_role: DeviceRole | None = await self.crud.get_by_field(
            self.session, "name", device_role.name
        )
        if local_device_role is not None:
            return_info = ERR_NUM_4009
            return_info.msg = f"Create device role failed, device role with name: `{device_role.name}` already exsits"
            return return_info
        new_device_role = DeviceRole(**device_role.dict(exclude_none=True))
        await self.session.add(new_device_role)
        await self.session.commit(new_device_role)
        return_info = ResponseMsg(data=new_device_role.id)
        return return_info

    @router.get("/device-roles/{id}")
    async def get_device_role(self, id: int) -> BaseResponse[schemas.DeviceRole]:
        local_device_role: DeviceRole | None = await self.session.get(DeviceRole, id)
        if local_device_role is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device role #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_device_role)
        return return_info

    @router.get("/device-roles")
    async def get_device_roles(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.DeviceRoleBase]]:
        results: List[DeviceRole] = await self.crud.get_all(
            self.session, q.limit, q.offset
        )
        count: int = self.session.execute(select(func.count(DeviceRole.id))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/device-roles/getList")
    async def get_device_roles_filter(
        self, device_role: schemas.DeviceRoleQuery
    ) -> BaseListResponse[List[schemas.DeviceRole]]:
        pass

    @router.put("/device-roles/{id}")
    async def update_device_role(
        self, device_role: schemas.DeviceRoleUpdate
    ) -> BaseResponse[int]:
        local_device_role: DeviceRole | None = await self.session.get(DeviceRole, id)
        if local_device_role is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Device role #{id} not found"
            return return_info
        try:
            await self.session.execute(
                update(DeviceRole)
                .where(DeviceRole.id == id)
                .values(**device_role.dict(exclude_none=True))
                .execute_options(synchronize_session="fetch")
            )
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Device Role with name `{device_role.name}` already exists"
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/device-roles/{id}")
    async def delete_device_role(self, id: int) -> BaseResponse[int]:
        local_device_role: DeviceRole | None = await self.crud.delete(self.session, id)
        if local_device_role is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete device role failed, device role #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/device-roles/deleteList")
    async def delete_device_roles(
        self, device_role: schemas.DeviceRoleBulkDelete
    ) -> BaseListResponse[List[int]]:
        results: List[DeviceRole] = await self.crud.delete_multi(
            self.session, device_role.ids
        )
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk device device role failed, device role #{device_role.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[d.id for d in results])
        return return_info


@cbv(router)
class InterfaceCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Interface)

    @router.post("/interfaces")
    async def create_interface(
        self, interface: schemas.InterfaceCreate
    ) -> BaseResponse[int]:
        new_interface = Interface(**interface.dict())
        try:
            await self.session.add(new_interface)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(e)
            return_info = ERR_NUM_4022
            return_info.data = str(e)
            return_info.msg = "Error creating interface, params error"
            return return_info
        return_info = ResponseMsg(data=new_interface.id)
        return return_info

    @router.get("/interfaces/{id}")
    async def get_interface(self, id: int) -> BaseResponse[schemas.InterfaceBase]:
        local_interface = await self.crud.get(self.session, id)
        if not local_interface:
            return_info = ERR_NUM_4004
            return_info.msg = f"Interface #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_interface)
        return return_info

    @router.get("/interfaces")
    async def get_interfaces(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.InterfaceBase]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = await self.session.execute(
            select(func.count(Interface.id))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/interfaces/getList")
    async def get_interfaces_filter(
        self, interface: schemas.InterfaceQuery
    ) -> BaseListResponse[List[schemas.Interface]]:
        pass

    @router.put("/interfaces/{id}")
    async def update_interface(
        self, interface: schemas.InterfaceUpdate
    ) -> BaseResponse[int]:
        pass

    @router.delete("/interfaces/{id}")
    async def delete_interface(self, id: int) -> BaseResponse[int]:
        local_interface: Interface = self.crud.delete(self.session, id)
        if not local_interface:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete interface failed, interface #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/interfaces/deleteList")
    async def bulk_delete_interface(
        self, interface: schemas.InterfaceBulkDelete
    ) -> BaseResponse[List[int]]:
        local_interface = await self.crud.delete_multi(self.session, interface.ids)
        if not local_interface:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk delete interface failed, interface #{id} not found"
            return return_info
        return_info = ResponseMsg(data=[d.id for d in local_interface])
        return return_info


@cbv(router)
class PlatformCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Platform)

    @router.post("/platforms")
    async def create_platform(
        self, platform: schemas.PlatformCreate
    ) -> BaseResponse[int]:
        new_platform = Platform(**platform.dict(exclude_none=True))
        try:
            await self.session.add(new_platform)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Created platform failed, platform with {platform.name} already exists"
            )
            return return_info
        return_info = ResponseMsg(new_platform.id)
        return return_info

    @router.get("/platforms/id")
    async def get_platform(self, id: int) -> BaseResponse[schemas.PlatformBase]:
        local_platform = await self.crud.get(self.session, id)
        if not local_platform:
            return_info = ERR_NUM_4004
            return_info.msg = f"Platform #{id} not found"
            return return_info
        return_info = ResponseMsg(local_platform)
        return return_info

    @router.get("/platforms")
    async def get_platforms(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.PlatformBase]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.session.execute(select(func.count(Platform.id))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/platforms/getList")
    async def get_platforms_filter(
        self, platforms: schemas.PlatformQuery
    ) -> BaseListResponse[List[schemas.PlatformBase]]:
        pass

    @router.put("/platforms/{id}")
    async def update_platform(
        self, id: int, platform: schemas.PlatformUpdate
    ) -> BaseResponse[int]:
        pass

    @router.delete("/platforms/{id}")
    async def delete_platform(self, id: int) -> BaseResponse[int]:
        local_platform = await self.crud.delete(self.session, id)
        if not local_platform:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete platform failed, platform #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/platforms/deleteList")
    async def bulk_delete_platforms(
        self, platform: schemas.PlatformBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, platform.ids)
        if results is None:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Bulk delete platform failed, platform #{platform.ids} not found"
            )
            return return_info
        return_info = ResponseMsg(data=[d.id for d in results])
        return_info.data = platform.ids
        return return_info
