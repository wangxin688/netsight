from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src._types import AuditLog, IdResponse, ListT
from src.cbv import cbv
from src.db import (
    AP,
    Device,
    DeviceEntity,
    DeviceGroup,
    DeviceType,
    Location,
    Platform,
    Rack,
    RackRole,
    Site,
    User,
    Vendor,
)
from src.db.dtobase import DtoBase
from src.dcim import schemas
from src.dcim.services import RackDto
from src.deps import auth, get_session

router = APIRouter()


@cbv(router)
class RackAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = RackDto(Rack)

    @router.post("/racks", operation_id="040b3088-1616-4c36-8db1-62152efe9e64")
    async def create_rack(self, rack: schemas.RackCreate) -> IdResponse:
        new_rack = await self.dto.create(self.session, rack)
        return IdResponse(id=new_rack.id)

    @router.put("/racks/{id}", operation_id="2ef4c329-7a64-47df-b493-de4dc1243fd7")
    async def update_rack(self, id: int, rack: schemas.RackUpdate) -> IdResponse:
        db_rack = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_rack, rack)
        return IdResponse(id=id)

    @router.get("/racks/{id}", operation_id="bf3247a8-7c82-41ee-95d2-57ddb8864b26")
    async def get_rack(self, id: int) -> schemas.Rack:
        db_rack = await self.dto.get_one_or_404(
            self.session,
            id,
            selectinload(Rack.rack_role).load_only(RackRole.id, RackRole.name),
            selectinload(Rack.site).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Rack.location).load_only(Location.id, Location.name),
            undefer_load=True,
        )
        return schemas.Rack.model_validate(db_rack)

    @router.get("/racks", operation_id="3d0c45e3-0be0-45b7-b36b-ef003421e374")
    async def get_racks(self, q: schemas.RackQuery = Depends()) -> ListT[schemas.Rack]:
        count, results = await self.dto.list_and_count(
            self.session,
            q,
            selectinload(Rack.rack_role).load_only(RackRole.id, RackRole.name),
            selectinload(Rack.site).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Rack.location).load_only(Location.id, Location.name),
        )
        return ListT(count=count, results=[schemas.Rack.model_validate(r) for r in results])

    @router.delete("/racks/{id}", operation_id="04ebcc08-82e7-40fc-91a4-09ae64784926")
    async def delete_rack(self, id: int) -> IdResponse:
        db_rack = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_rack)
        return IdResponse(id=id)

    @router.get("/racks/{id}/auditlogs", operation_id="58f32b45-c3ec-4201-8a93-ba373d9084c9")
    async def get_rack_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class VendorAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(Vendor)

    @router.post("/vendors", operation_id="e56edca5-f270-494f-894b-e80b76ed6e5e")
    async def create_vendor(self, vendor: schemas.VendorCreate) -> IdResponse:
        new_vendor = await self.dto.create(self.session, vendor)
        return IdResponse(id=new_vendor.id)

    @router.put("/vendors/{id}", operation_id="f79ca68c-1768-4e6e-a568-020a6ff844e5")
    async def update_vendor(self, id: int, vendor: schemas.VendorUpdate) -> IdResponse:
        db_vendor = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_vendor, vendor)
        return IdResponse(id=id)

    @router.get("/vendors/{id}", operation_id="f7500762-95de-4125-87b7-8b9dc4cb4201")
    async def get_vendor(self, id: int) -> schemas.Vendor:
        db_vendor = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.Vendor.model_validate(db_vendor)

    @router.get("/vendors", operation_id="a30fb40d-04b3-41fd-a7ba-3040270a191b")
    async def get_vendors(self, q: schemas.VendorQuery = Depends()) -> ListT[schemas.Vendor]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.Vendor.model_validate(r) for r in results])

    @router.delete("/vendors/{id}", operation_id="f9b8b6d9-6b7a-4c0e-8b6a-4b0e8b6d9f9b")
    async def delete_vendor(self, id: int) -> IdResponse:
        db_vendor = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_vendor)
        return IdResponse(id=id)

    @router.get("/vendors/{id}/auditlogs", operation_id="1cc7297f-b208-4381-8ef1-97ad092a82cb")
    async def get_vendor_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class DeviceTypeAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(DeviceType)

    @router.post("/device-types", operation_id="cea5008c-0a32-4bdb-9c17-709230168e2b")
    async def create_device_type(self, device_type: schemas.DeviceTypeCreate) -> IdResponse:
        new_device_type = await self.dto.create(self.session, device_type)
        return IdResponse(id=new_device_type.id)

    @router.put("/device-types/{id}", operation_id="505c9f48-1880-43cd-845b-c517a22d4fd5")
    async def update_device_type(self, id: int, device_type: schemas.DeviceTypeUpdate) -> IdResponse:
        db_device_type = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_device_type, device_type)
        return IdResponse(id=id)

    @router.get("/device-types/{id}", operation_id="653e2c8f-11a8-4e04-87c1-a674c0be55d1")
    async def get_device_type(self, id: int) -> schemas.DeviceType:
        db_device_type = await self.dto.get_one_or_404(
            self.session,
            id,
            selectinload(DeviceType.vendor).load_only(Vendor.id, Vendor.name),
            selectinload(DeviceType.platform).load_only(Platform.id, Platform.name, Platform.netmiko_driver),
            undefer_load=True,
        )
        return schemas.DeviceType.model_validate(db_device_type)

    @router.get("/device-types", operation_id="e67dcd2d-7b9c-4701-856c-55f95d2925a5")
    async def get_device_types(self, q: schemas.DeviceTypeQuery = Depends()) -> ListT[schemas.DeviceType]:
        count, results = await self.dto.list_and_count(
            self.session,
            q,
            selectinload(DeviceType.vendor).load_only(Vendor.id, Vendor.name),
            selectinload(DeviceType.platform).load_only(Platform.id, Platform.name, Platform.netmiko_driver),
        )
        return ListT(count=count, results=[schemas.DeviceType.model_validate(r) for r in results])

    @router.delete("/device-types/{id}", operation_id="551aef93-9346-4db6-803c-14d88c2b69c7")
    async def delete_device_type(self, id: int) -> IdResponse:
        db_device_type = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_device_type)
        return IdResponse(id=id)

    @router.get("/device-types/{id}/auditlogs", operation_id="1b376206-f410-410c-87a9-e31d6ff2ae87")
    async def get_device_type_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class PlatformAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(Platform)

    @router.post("/platforms", operation_id="38e18494-e38c-4060-962f-64dfd37a61af")
    async def create_platform(self, platform: schemas.PlatformCreate) -> IdResponse:
        new_platform = await self.dto.create(self.session, platform)
        return IdResponse(id=new_platform.id)

    @router.put("/platforms/{id}", operation_id="a452765a-91b7-4b37-bca1-11864e1be028")
    async def update_platform(self, id: int, platform: schemas.PlatformUpdate) -> IdResponse:
        db_platform = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_platform, platform)
        return IdResponse(id=id)

    @router.get("/platforms/{id}", operation_id="9324bde0-600f-4470-98da-343fc498289c")
    async def get_platform(self, id: int) -> schemas.Platform:
        db_platform = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.Platform.model_validate(db_platform)

    @router.get("/platforms", operation_id="d47d8d64-f8cc-4ddc-9db9-51d6a1f3b9e3")
    async def get_platforms(self, q: schemas.PlatformQuery = Depends()) -> ListT[schemas.Platform]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.Platform.model_validate(r) for r in results])

    @router.delete("/platforms/{id}", operation_id="73a00be4-be83-4d24-a034-d36926bae8e1")
    async def delete_platform(self, id: int) -> IdResponse:
        db_platform = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_platform)
        return IdResponse(id=id)

    @router.get("/platforms/{id}/auditlogs", operation_id="62ca0f32-56b3-47bb-838f-20402c2bb1f4")
    async def get_platform_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class DeviceAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(Device)

    @router.post("/devices", operation_id="8e4357aa-9de9-4daf-858c-78f92fbd7160")
    async def create_device(self, device: schemas.DeviceCreate) -> IdResponse:
        new_device = await self.dto.create(self.session, device)
        return IdResponse(id=new_device.id)

    @router.put("/devices/{id}", operation_id="7770767a-1862-45ea-9352-375e8b83e3a0")
    async def update_device(self, id: int, device: schemas.DeviceUpdate) -> IdResponse:
        db_device = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_device, device)
        return IdResponse(id=id)

    @router.get("/devices/{id}", operation_id="b6ac2c56-099f-4e4c-b541-98c12a3022e7")
    async def get_device(self, id: int) -> schemas.Device:
        db_device = await self.dto.get_one_or_404(
            self.session,
            id,
            selectinload(Device.device_type).selectinload(DeviceType.platform).selectinload(DeviceType.vendor),
            undefer_load=True,
        )
        return schemas.Device.model_validate(db_device)

    @router.get("/devices", operation_id="2474bb19-b2a6-46ec-95c8-e03d8bab0d76")
    async def get_devices(self, q: schemas.DeviceQuery = Depends()) -> ListT[schemas.Device]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.Device.model_validate(r) for r in results])

    @router.delete("/devices/{id}", operation_id="5c7fe859-ca20-415d-b1d5-0020bf5a4c23")
    async def delete_device(self, id: int) -> IdResponse:
        db_device = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_device)
        return IdResponse(id=id)

    @router.get("/devices/{id}/auditlogs", operation_id="b4d46b38-c3d9-4e93-9e46-7211b1884e69")
    async def get_device_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class DeviceEntityAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(DeviceEntity)

    @router.post("/device-entities", operation_id="b998bbdf-0956-4e09-998a-9e1d8c3c8f39")
    async def create_device_entity(self, device_entity: schemas.DeviceEntityCreate) -> IdResponse:
        new_device_entity = await self.dto.create(self.session, device_entity)
        return IdResponse(id=new_device_entity.id)

    @router.put("/device-entities/{id}", operation_id="1107ccbf-404d-452d-9516-b5b841cfbf21")
    async def update_device_entity(self, id: int, device_entity: schemas.DeviceEntityUpdate) -> IdResponse:
        db_device_entity = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_device_entity, device_entity)
        return IdResponse(id=id)

    @router.get("/device-entities/{id}", operation_id="45a60826-778a-46af-b716-5d68cbae6ce2")
    async def get_device_entity(self, id: int) -> schemas.DeviceEntity:
        db_device_entity = await self.dto.get_one_or_404(self.session, id)
        return schemas.DeviceEntity.model_validate(db_device_entity)

    @router.get("/device-entities", operation_id="1976392a-1013-4c5a-ac97-80b500b97d9f")
    async def get_device_entities(self, q: schemas.DeviceEntityQuery = Depends()) -> ListT[schemas.DeviceEntity]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.DeviceEntity.model_validate(r) for r in results])

    @router.delete("/device-entities/{id}", operation_id="65d00786-dc91-495b-b1dc-1ae42af99de7")
    async def delete_device_entity(self, id: int) -> IdResponse:
        db_device_entity = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_device_entity)
        return IdResponse(id=id)

    @router.get("/device-entities/{id}/auditlogs", operation_id="9b077eb6-4119-420f-a51f-727b63f748be")
    async def get_device_entity_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class DeviceGroupAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(DeviceGroup)

    @router.post("/device-groups", operation_id="a70c2ef2-8591-4e67-a490-473c9e28b8ea")
    async def create_device_group(self, device_group: schemas.DeviceGroupCreate) -> IdResponse:
        new_device_group = await self.dto.create(self.session, device_group)
        return IdResponse(id=new_device_group.id)

    @router.put("/device-groups/{id}", operation_id="d0133321-d06f-4ebb-baba-ffa1fc96bafd")
    async def update_device_group(self, id: int, device_group: schemas.DeviceGroupUpdate) -> IdResponse:
        db_device_group = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_device_group, device_group)
        return IdResponse(id=id)

    @router.get("/device-groups/{id}", operation_id="4a6a2560-bde2-43f2-be3e-8c370d653ac2")
    async def get_device_group(self, id: int) -> schemas.DeviceGroup:
        db_device_group = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.DeviceGroup.model_validate(db_device_group)

    @router.get("/device-groups", operation_id="81d1172e-950b-4134-9b2f-9a5cd56bf985")
    async def get_device_groups(self, q: schemas.DeviceGroupQuery = Depends()) -> ListT[schemas.DeviceGroup]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.DeviceGroup.model_validate(r) for r in results])

    @router.delete("/device-groups/{id}", operation_id="a782f23c-a9b4-4b1d-a276-c0a94f71a127")
    async def delete_device_group(self, id: int) -> IdResponse:
        db_device_group = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_device_group)
        return IdResponse(id=id)

    @router.get("/device-groups/{id}/auditlogs", operation_id="2ac1c868-a0b7-4b86-9f6a-42b77a47b96c")
    async def get_device_group_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class APAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(AP)

    @router.post("/aps", operation_id="deed76e4-3575-4d9d-8922-90684ad36e73")
    async def create_ap(self, ap: schemas.APCreate) -> IdResponse:
        new_ap = await self.dto.create(self.session, ap)
        return IdResponse(id=new_ap.id)

    @router.put("/aps/{id}", operation_id="af348d5b-8adf-4611-a835-8028a4c9178d")
    async def update_ap(self, id: int, ap: schemas.APUpdate) -> IdResponse:
        db_ap = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_ap, ap)
        return IdResponse(id=id)

    @router.get("/aps/{id}", operation_id="d1ea839c-0181-4cbf-97af-c99793ede788")
    async def get_ap(self, id: int) -> schemas.AP:
        db_ap = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.AP.model_validate(db_ap)

    @router.get("/aps", operation_id="b3fab230-cc6f-4bbd-9671-09618a36114b")
    async def get_aps(self, q: schemas.APQuery = Depends()) -> ListT[schemas.AP]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.AP.model_validate(r) for r in results])

    @router.delete("/aps/{id}", operation_id="cfe0a299-9462-413f-a57e-d566a8691cda")
    async def delete_ap(self, id: int) -> IdResponse:
        db_ap = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_ap)
        return IdResponse(id=id)
