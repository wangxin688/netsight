from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth.models import User
from src.api.base import BaseListResponse, BaseResponse, CommonQueryParams
from src.api.dcim import schemas
from src.api.dcim.models import Region, Site
from src.api.deps import get_current_user, get_session
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_0, ERR_NUM_4004, ERR_NUM_4009
from src.utils.loggers import logger

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class RegionCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/regions")
    async def create_region(self, region: schemas.RegionCreate) -> BaseResponse[int]:
        try:
            new_region = Region(**region.dict(exclude_none=True))
            self.session.add(new_region)
            await self.session.commit()
            await self.session.flush()
        except SQLAlchemyError:
            return {
                "code": ERR_NUM_4009.code,
                "data": None,
                "msg": f"Region with name: {region.name} already exists",
            }
        finally:
            return_info = ERR_NUM_0
            return_info.data = new_region.id
            return return_info

    @router.get("/regions/{id}")
    async def get_region(self, id: int) -> BaseResponse[schemas.Region]:
        results = (
            (await self.session.execute(select(Region).where(Region.id == id)))
            .scalars()
            .first()
        )
        return_info = ERR_NUM_0
        return_info.data = results
        return return_info

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
        return return_info

    @router.put("/regions/{id}")
    async def update_region(
        self, id: int, region: schemas.RegionUpdate
    ) -> BaseResponse[int]:
        local_result: Region | None = (
            (await self.session.execute(select(Region).where(Region.id == id)))
            .scalars()
            .first()
        )
        if not local_result:
            return ERR_NUM_4004
        try:
            stmt = (
                update(Region)
                .where(Region.id == id)
                .values(**region.dict(exclude_none=True))
                .execute_options(synchronize_session="fetch")
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return_info = ERR_NUM_0
            return_info.data = id
            return return_info
        except SQLAlchemyError as e:
            logger.error(e)
            return {
                "code": ERR_NUM_4009.code,
                "data": None,
                "msg": f"Region with name '{region.name}' already exists",
            }

    @router.delete("/regions/{id}")
    async def delete_region(self, id: int) -> BaseResponse[int]:
        try:
            stmt = delete(Region).where(Region.id == id)
            await self.session.execute(stmt)
            await self.session.commit()
            return_info = ERR_NUM_0
            return_info.data = id
            return return_info
        except SQLAlchemyError as e:
            logger.error(e)
            return {
                "code": ERR_NUM_4004.code,
                "data": None,
                "msg": f"Region #{id} not existed",
            }


@cbv(router)
class SiteCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/sites")
    async def create_site(
        self, site: schemas.SiteCreate
    ) -> BaseListResponse[List[schemas.Region]]:
        pass

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
        pass

    @router.delete("/sites/{id}")
    async def delete_site(
        self,
        id: int,
    ) -> BaseResponse[int]:
        pass


@cbv(router)
class LocationCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/locations")
    async def create_location(
        self, region: schemas.LocationCreate
    ) -> BaseResponse[int]:
        pass

    @router.get("/locations/{id}")
    async def get_location(self, id: int) -> BaseResponse[schemas.Location]:
        pass

    @router.get("/locations")
    async def get_locations(
        self, location: schemas.LocationQuery
    ) -> BaseListResponse[List[schemas.Location]]:
        pass

    @router.put("/locations/{id}")
    async def update_location(
        self, id: int, region: schemas.LocationUpdate
    ) -> BaseResponse[int]:
        pass

    @router.delete("/locations/{id}")
    async def delete_location(self, id: int) -> BaseResponse[int]:
        pass


@cbv(router)
class RackRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/rack-roles")
    async def create_rack_role(
        self, region: schemas.RackRoleCreate
    ) -> BaseResponse[int]:
        pass

    @router.get("/rack-roles/{id}")
    async def get_rack_role(self, id: int) -> BaseResponse[schemas.RackRole]:
        pass

    @router.get("/rack-roles")
    async def get_rack_roles(
        self, rack_role: schemas.RackRoleQuery
    ) -> BaseListResponse[List[schemas.RackRole]]:
        pass

    @router.put("/rack-roles/{id}")
    async def update_rack_role(
        self, id: int, rack_role: schemas.RackRoleUpdate
    ) -> BaseResponse[int]:
        pass

    @router.delete("/rack-roles/{id}")
    async def delete_rack_role(self, id: int) -> BaseResponse[int]:
        pass


@cbv(router)
class RackCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/racks")
    async def create_rack(self, rack: schemas.RackCreate) -> BaseResponse[int]:
        pass

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
        pass

    @router.get("/manufacturers/{id}")
    async def get_manufacturer(self, id: int) -> BaseResponse[schemas.Manufacturer]:
        pass

    @router.get("/manufacturers")
    async def get_manufacturers(
        self, manufacturer: schemas.ManufacturerQuery
    ) -> BaseListResponse[List[schemas.Manufacturer]]:
        pass

    @router.put("/manufacturers/{id}")
    async def update_manufacturer(
        self, id: int, manufacturer: schemas.ManufacturerUpdate
    ) -> BaseResponse[int]:
        pass

    @router.delete("/manufacturers/{id}")
    async def delete_manufacturer(self, id: int) -> BaseResponse[int]:
        pass


@cbv(router)
class DeviceTypeCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/device-types")
    async def create_device_type(
        self, device_type: schemas.DeviceTypeCreate
    ) -> BaseResponse[int]:
        pass

    @router.get("/device-types/{id}")
    async def get_device_type(self, id: int) -> BaseResponse[schemas.DeviceType]:
        pass

    @router.get("/device-types")
    async def get_device_types(
        self, device_type: schemas.DeviceTypeQuery
    ) -> BaseListResponse[List[schemas.DeviceType]]:
        pass

    @router.put("/device-types/{id}")
    async def update_device_type(
        self, device_type: schemas.DeviceTypeUpdate
    ) -> BaseResponse[int]:
        pass

    @router.delete("/device-types/{id}")
    async def delete_device_type(self, id: int) -> BaseResponse[int]:
        pass


@cbv(router)
class DeviceRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)

    @router.post("/device-roles")
    async def create_device_role(
        self, device_role: schemas.DeviceRoleCreate
    ) -> BaseResponse[int]:
        pass

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
        pass

    @router.delete("/device-roles/{id}")
    async def delete_device_role(self, id: int) -> BaseResponse[int]:
        pass


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
