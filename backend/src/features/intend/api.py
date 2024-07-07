from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.utils.cbv import cbv
from src.features._types import IdResponse, ListT
from src.features.admin.models import User
from src.features.deps import auth, get_session
from src.features.intend import schemas, services
from src.features.intend.models import DeviceType, Manufacturer, Platform

router = APIRouter()


@cbv(router)
class CircuitTypeAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.circuit_type_service

    @router.post("/circuit-types", operation_id="be8f6f87-90f4-429d-8b80-85a3816bb466")
    async def create_circuit_type(self, circuit_type: schemas.CircuitTypeCreate) -> IdResponse:
        new_obj = await self.service.create(self.session, circuit_type)
        return IdResponse(id=new_obj.id)

    @router.put("/circuit-types/{id}", operation_id="f59b05a7-21b4-4821-8c8c-0ae1736697a8")
    async def update_circuit_type(self, id: int, circuit_type: schemas.CircuitTypeUpdate) -> IdResponse:
        db_obj = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_obj, circuit_type)
        return IdResponse(id=id)

    @router.get("/circuit-types/{id}", operation_id="1c098d58-589e-497f-ac14-90fde0c9e34b")
    async def get_circuit_type(self, id: int) -> schemas.CircuitType:
        db_obj = await self.service.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.CircuitType.model_validate(db_obj)

    @router.get("/circuit-types", operation_id="da40d788-6220-4159-bfdc-4c9371e9c18e")
    async def get_circuit_types(self, q: schemas.CircuitTypeQuery = Depends()) -> ListT[schemas.CircuitType]:
        count, results = await self.service.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.CircuitType.model_validate(r) for r in results])

    @router.delete("/circuit-types/{id}", operation_id="2648dce5-b9dd-4275-9cb8-de6619e3bcf2")
    async def delete_circuit_type(self, id: int) -> IdResponse:
        db_obj = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_obj)
        return IdResponse(id=id)


@cbv(router)
class DeviceRoleAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.device_role_service

    @router.post("/device-roles", operation_id="b266343a-2832-4984-97ca-5bcb9b1f13fc")
    async def create_device_role(self, device_role: schemas.DeviceRoleCreate) -> IdResponse:
        new_obj = await self.service.create(self.session, device_role)
        return IdResponse(id=new_obj.id)

    @router.put("/device-roles/{id}", operation_id="f43827ee-d502-4ecf-b22d-e91a562c4461")
    async def update_device_role(self, id: int, device_role: schemas.DeviceRoleUpdate) -> IdResponse:
        db_obj = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_obj, device_role)
        return IdResponse(id=id)

    @router.get("/device-roles/{id}", operation_id="9644dc6a-f419-434b-990c-2339f37f02a6")
    async def get_device_role(self, id: int) -> schemas.DeviceRole:
        db_obj = await self.service.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.DeviceRole.model_validate(db_obj)

    @router.get("/device-roles", operation_id="5f670dd6-eba5-49f4-b00e-05ee430625b5")
    async def get_device_roles(self, q: schemas.DeviceRoleQuery = Depends()) -> ListT[schemas.DeviceRole]:
        count, results = await self.service.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.DeviceRole.model_validate(r) for r in results])

    @router.delete("/device-roles/{id}", operation_id="a2d82d5f-0c8a-472a-b0eb-1bafe955ccd5")
    async def delete_device_role(self, id: int) -> IdResponse:
        db_obj = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_obj)
        return IdResponse(id=id)


@cbv(router)
class IPRoleAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.ip_role_service

    @router.post("/ip-roles", operation_id="6adadd9a-f2d9-49da-824f-58df420ab35e")
    async def create_ip_role(self, ip_role: schemas.IPRoleCreate) -> IdResponse:
        new_obj = await self.service.create(self.session, ip_role)
        return IdResponse(id=new_obj.id)

    @router.put("/ip-roles/{id}", operation_id="b582d431-db75-47fc-840b-0061f3cd1a2c")
    async def update_ip_role(self, id: int, ip_role: schemas.IPRoleUpdate) -> IdResponse:
        db_obj = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_obj, ip_role)
        return IdResponse(id=id)

    @router.get("/ip-roles/{id}", operation_id="e37f0bc5-2e54-4cae-8f8b-bc226f61f862")
    async def get_ip_role(self, id: int) -> schemas.IPRole:
        db_obj = await self.service.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.IPRole.model_validate(db_obj)

    @router.get("/ip-roles", operation_id="333be12d-5f84-46ca-af12-2790708d9ef9")
    async def get_ip_roles(self, q: schemas.IPRoleQuery = Depends()) -> ListT[schemas.IPRole]:
        count, results = await self.service.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.IPRole.model_validate(r) for r in results])

    @router.delete("/ip-roles/{id}", operation_id="188cb57e-1218-47c8-bd0d-fbe7a3b951ec")
    async def delete_ip_role(self, id: int) -> IdResponse:
        db_obj = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_obj)
        return IdResponse(id=id)


@cbv(router)
class PlatformAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.platform_service

    @router.post("/platforms", operation_id="38e18494-e38c-4060-962f-64dfd37a61af")
    async def create_platform(self, platform: schemas.PlatformCreate) -> IdResponse:
        new_platform = await self.service.create(self.session, platform)
        return IdResponse(id=new_platform.id)

    @router.put("/platforms/{id}", operation_id="a452765a-91b7-4b37-bca1-11864e1be028")
    async def update_platform(self, id: int, platform: schemas.PlatformUpdate) -> IdResponse:
        db_platform = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_platform, platform)
        return IdResponse(id=id)

    @router.get("/platforms/{id}", operation_id="9324bde0-600f-4470-98da-343fc498289c")
    async def get_platform(self, id: int) -> schemas.Platform:
        db_platform = await self.service.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.Platform.model_validate(db_platform)

    @router.get("/platforms", operation_id="d47d8d64-f8cc-4ddc-9db9-51d6a1f3b9e3")
    async def get_platforms(self, q: schemas.PlatformQuery = Depends()) -> ListT[schemas.Platform]:
        count, results = await self.service.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.Platform.model_validate(r) for r in results])

    @router.delete("/platforms/{id}", operation_id="73a00be4-be83-4d24-a034-d36926bae8e1")
    async def delete_platform(self, id: int) -> IdResponse:
        db_platform = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_platform)
        return IdResponse(id=id)


@cbv(router)
class ManufacturerAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.manufacturer_service

    @router.post("/manufacturers", operation_id="e56edca5-f270-494f-894b-e80b76ed6e5e")
    async def create_manufacturer(self, manufacturer: schemas.ManufacturerCreate) -> IdResponse:
        new_manufacturer = await self.service.create(self.session, manufacturer)
        return IdResponse(id=new_manufacturer.id)

    @router.put("/manufacturers/{id}", operation_id="f79ca68c-1768-4e6e-a568-020a6ff844e5")
    async def update_manufacturer(self, id: int, manufacturer: schemas.ManufacturerUpdate) -> IdResponse:
        db_manufacturer = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_manufacturer, manufacturer)
        return IdResponse(id=id)

    @router.get("/manufacturers/{id}", operation_id="f7500762-95de-4125-87b7-8b9dc4cb4201")
    async def get_manufacturer(self, id: int) -> schemas.Manufacturer:
        db_manufacturer = await self.service.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.Manufacturer.model_validate(db_manufacturer)

    @router.get("/manufacturers", operation_id="a30fb40d-04b3-41fd-a7ba-3040270a191b")
    async def get_manufacturers(self, q: schemas.ManufacturerQuery = Depends()) -> ListT[schemas.Manufacturer]:
        count, results = await self.service.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.Manufacturer.model_validate(r) for r in results])

    @router.delete("/manufacturers/{id}", operation_id="f9b8b6d9-6b7a-4c0e-8b6a-4b0e8b6d9f9b")
    async def delete_manufacturer(self, id: int) -> IdResponse:
        db_manufacturer = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_manufacturer)
        return IdResponse(id=id)


@cbv(router)
class DeviceTypeAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.device_type_service

    @router.post("/device-types", operation_id="cea5008c-0a32-4bdb-9c17-709230168e2b")
    async def create_device_type(self, device_type: schemas.DeviceTypeCreate) -> IdResponse:
        new_device_type = await self.service.create(self.session, device_type)
        return IdResponse(id=new_device_type.id)

    @router.put("/device-types/{id}", operation_id="505c9f48-1880-43cd-845b-c517a22d4fd5")
    async def update_device_type(self, id: int, device_type: schemas.DeviceTypeUpdate) -> IdResponse:
        db_device_type = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_device_type, device_type)
        return IdResponse(id=id)

    @router.get("/device-types/{id}", operation_id="653e2c8f-11a8-4e04-87c1-a674c0be55d1")
    async def get_device_type(self, id: int) -> schemas.DeviceType:
        db_device_type = await self.service.get_one_or_404(
            self.session,
            id,
            selectinload(DeviceType.manufacturer).load_only(Manufacturer.id, Manufacturer.name),
            selectinload(DeviceType.platform).load_only(Platform.id, Platform.name, Platform.netmiko_driver),
            undefer_load=True,
        )
        return schemas.DeviceType.model_validate(db_device_type)

    @router.get("/device-types", operation_id="e67dcd2d-7b9c-4701-856c-55f95d2925a5")
    async def get_device_types(self, q: schemas.DeviceTypeQuery = Depends()) -> ListT[schemas.DeviceType]:
        count, results = await self.service.list_and_count(
            self.session,
            q,
            selectinload(DeviceType.manufacturer).load_only(Manufacturer.id, Manufacturer.name),
            selectinload(DeviceType.platform).load_only(Platform.id, Platform.name, Platform.netmiko_driver),
        )
        return ListT(count=count, results=[schemas.DeviceType.model_validate(r) for r in results])

    @router.delete("/device-types/{id}", operation_id="551aef93-9346-4db6-803c-14d88c2b69c7")
    async def delete_device_type(self, id: int) -> IdResponse:
        db_device_type = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_device_type)
        return IdResponse(id=id)
