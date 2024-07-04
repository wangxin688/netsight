from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.repositories import BaseRepository
from src.core.utils.cbv import cbv
from src.features._types import AuditLog, IdResponse, ListT
from src.features.admin.models import User
from src.features.dcim import schemas
from src.features.dcim.models import Device
from src.features.intend.models import DeviceType
from src.features.deps import auth, get_session

router = APIRouter()


@cbv(router)
class DeviceAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = BaseRepository(Device)

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
            selectinload(Device.device_type).selectinload(DeviceType.platform).selectinload(DeviceType.manufacturer),
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
