from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from netsight.core.utils.cbv import cbv
from netsight.features._types import AuditLog, IdResponse, ListT
from netsight.features.admin.models import User
from netsight.features.dcim import schemas, services
from netsight.features.dcim.models import Device
from netsight.features.deps import auth, get_session
from netsight.features.intend.models import DeviceRole, DeviceType, Manufacturer, Platform
from netsight.features.org.models import Location, Site

router = APIRouter()


@cbv(router)
class DeviceAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.device_service

    @router.post("/devices", operation_id="8e4357aa-9de9-4daf-858c-78f92fbd7160")
    async def create_device(self, device: schemas.DeviceCreate) -> IdResponse:
        new_device = await self.service.create(self.session, device)
        return IdResponse(id=new_device.id)

    @router.put("/devices/{id}", operation_id="7770767a-1862-45ea-9352-375e8b83e3a0")
    async def update_device(self, id: int, device: schemas.DeviceUpdate) -> IdResponse:
        db_device = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_device, device)
        return IdResponse(id=id)

    @router.get("/devices/{id}", operation_id="b6ac2c56-099f-4e4c-b541-98c12a3022e7")
    async def get_device(self, id: int) -> schemas.Device:
        db_device = await self.service.get_one_or_404(
            self.session,
            id,
            selectinload(Device.device_type).load_only(DeviceType.id, DeviceType.name),
            selectinload(DeviceType.platform).load_only(Platform.id, Platform.name),
            selectinload(DeviceType.manufacturer).load_only(Manufacturer.id, Manufacturer.name),
            selectinload(Device.device_role).load_only(DeviceRole.id, DeviceRole.name),
            selectinload(Device.location).load_only(Location.id, Location.name),
            selectinload(Device.site).load_only(Site.id, Site.name),
            selectinload(Device.created_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(Device.updated_by).load_only(User.id, User.name, User.email, User.avatar),
            undefer_load=True,
        )
        return schemas.Device.model_validate(db_device)

    @router.get("/devices", operation_id="2474bb19-b2a6-46ec-95c8-e03d8bab0d76")
    async def get_devices(self, q: schemas.DeviceQuery = Depends()) -> ListT[schemas.DeviceList]:
        count, results = await self.service.list_and_count(
            self.session,
            q,
            selectinload(Device.device_type).load_only(DeviceType.id, DeviceType.name),
            selectinload(DeviceType.platform).load_only(Platform.id, Platform.name),
            selectinload(DeviceType.manufacturer).load_only(Manufacturer.id, Manufacturer.name),
            selectinload(Device.device_role).load_only(DeviceRole.id, DeviceRole.name),
            selectinload(Device.location).load_only(Location.id, Location.name),
            selectinload(Device.site).load_only(Site.id, Site.name),
        )
        return ListT(count=count, results=[schemas.DeviceList.model_validate(r) for r in results])

    @router.delete("/devices/{id}", operation_id="5c7fe859-ca20-415d-b1d5-0020bf5a4c23")
    async def delete_device(
        self,
        id: int = Path(
            ge=0,
            description="When device is deleted, device related data, such as interfaces, stacks, modules and etc will also be deleted",
        ),
    ) -> IdResponse:
        db_device = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_device)
        return IdResponse(id=id)

    @router.get("/devices/{id}/auditlogs", operation_id="b4d46b38-c3d9-4e93-9e46-7211b1884e69")
    async def get_device_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.service.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])

    @router.post("/devices/{id}/modules", operation_id="144c5bbb-4344-46a7-87f5-2a855a3a589c")
    async def sync_device_modules(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/modules", operation_id="97e99f2d-40e7-459c-8362-5626b612a01d")
    async def get_device_modules(self, id: int) -> list[schemas.DeviceModule]: ...

    @router.post("/devices/{id}/stacks", operation_id="71342e92-ded8-44f2-a0cf-2d910f592115")
    async def sync_device_stacks(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/stacks", operation_id="9f649f2d-db10-47e8-a4ce-227e24678892")
    async def get_device_stacks(self, id: int) -> list[schemas.DeviceStack]: ...

    @router.post("/devices/{id}/interfaces", operation_id="3b32c20b-546a-44f8-9e36-a0cdba6a6820")
    async def sync_device_interfaces(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/interfaces", operation_id="557b29fe-7a70-4e3f-8f68-c3d3adbaa284")
    async def get_device_interfaces(self, id: int) -> list[schemas.Interface]: ...

    @router.post("/devices/{id}/equipments", operation_id="a5e8f9a3-1c6a-4f8f-9a6e-9f1f9b9b9b9b")
    async def sync_device_equipments(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/equipment", operation_id="94a6902f-9b79-44fe-bebf-03a36c191f04")
    async def get_device_equipment(self, id: int) -> list[schemas.DeviceEquipment]: ...

    @router.post("/devices/{id}/configurations", operation_id="dbcfb412-10a6-4811-a703-140c1a3c68ac")
    async def configuration_backup(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/configurations", operation_id="933fe8b9-005d-40df-b918-59f5005b6747")
    async def get_device_configurations(self, id: int) -> list[schemas.Configuration]: ...

    @router.post("/devices/{id}/topology", operation_id="f9b7b9e0-9b9b-4f4f-9b9b-9b9b9b9b9b9b")
    async def sync_device_topology(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/topology", operation_id="51df6271-1cc2-47f3-b76b-8c5033db41f4")
    async def get_device_topology(self, id: int) -> list[schemas.Topology]: ...

    @router.post("/devices/{id}/mac-address-tables", operation_id="7f848f5d-c75f-4fe1-b7f4-5ae734e9cb52")
    async def sync_device_mac_address_table(self, id: int) -> IdResponse: ...

    @router.get("/devices/{id}/mac-address-tables", operation_id="6289d1b5-400a-43a5-bade-7b0fe38d6d49")
    async def get_device_mac_address_table(self, id: int) -> list[schemas.MacAddress]: ...

    @router.get("/devices/{id}/routes", operation_id="cea3646d-12f9-4d93-8549-8f2ac5ca8c99")
    async def get_device_routes(self, id: int) -> list[schemas.Route]: ...
