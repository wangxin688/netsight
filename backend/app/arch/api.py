from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app._types import AuditLog, IdResponse, ListT
from app.arch import schemas
from app.db import CircuitType, DeviceRole, IPRole, RackRole, User
from app.db.dtobase import DtoBase
from app.deps import auth, get_session
from app.utils.cbv import cbv

router = APIRouter()


@cbv(router)
class CircuitTypeAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(CircuitType)

    @router.post("/circuit-types", operation_id="be8f6f87-90f4-429d-8b80-85a3816bb466")
    async def create_circuit_type(self, circuit_type: schemas.CircuitTypeCreate) -> IdResponse:
        new_obj = await self.dto.create(self.session, circuit_type)
        return IdResponse(id=new_obj.id)

    @router.put("/circuit-types/{id}", operation_id="f59b05a7-21b4-4821-8c8c-0ae1736697a8")
    async def update_circuit_type(self, id: int, circuit_type: schemas.CircuitTypeUpdate) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_obj, circuit_type)
        return IdResponse(id=id)

    @router.get("/circuit-types/{id}", operation_id="1c098d58-589e-497f-ac14-90fde0c9e34b")
    async def get_circuit_type(self, id: int) -> schemas.CircuitType:
        db_obj = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.CircuitType.model_validate(db_obj)

    @router.get("/circuit-types", operation_id="da40d788-6220-4159-bfdc-4c9371e9c18e")
    async def get_circuit_types(self, q: schemas.CircuitTypeQuery = Depends()) -> ListT[schemas.CircuitType]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.CircuitType.model_validate(r) for r in results])

    @router.delete("/circuit-types/{id}", operation_id="2648dce5-b9dd-4275-9cb8-de6619e3bcf2")
    async def delete_circuit_type(self, id: int) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_obj)
        return IdResponse(id=id)

    @router.get("/circuit-types/{id}/auditlogs", operation_id="ab82f114-e360-47f3-9d31-4429b29ed2f5")
    async def get_circuit_type_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class DeviceRoleAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(DeviceRole)

    @router.post("/device-roles", operation_id="b266343a-2832-4984-97ca-5bcb9b1f13fc")
    async def create_device_role(self, device_role: schemas.DeviceRoleCreate) -> IdResponse:
        new_obj = await self.dto.create(self.session, device_role)
        return IdResponse(id=new_obj.id)

    @router.put("/device-roles/{id}", operation_id="f43827ee-d502-4ecf-b22d-e91a562c4461")
    async def update_device_role(self, id: int, device_role: schemas.DeviceRoleUpdate) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_obj, device_role)
        return IdResponse(id=id)

    @router.get("/device-roles/{id}", operation_id="9644dc6a-f419-434b-990c-2339f37f02a6")
    async def get_device_role(self, id: int) -> schemas.DeviceRole:
        db_obj = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.DeviceRole.model_validate(db_obj)

    @router.get("/device-roles", operation_id="5f670dd6-eba5-49f4-b00e-05ee430625b5")
    async def get_device_roles(self, q: schemas.DeviceRoleQuery = Depends()) -> ListT[schemas.DeviceRole]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.DeviceRole.model_validate(r) for r in results])

    @router.delete("/device-roles/{id}", operation_id="a2d82d5f-0c8a-472a-b0eb-1bafe955ccd5")
    async def delete_device_role(self, id: int) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_obj)
        return IdResponse(id=id)

    @router.get("/device-roles/{id}/auditlogs", operation_id="b5443838-9e09-4cfe-97d5-8bf7285399be")
    async def get_device_role_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class RackRoleAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(RackRole)

    @router.post("/rack-roles", operation_id="60f2f8e2-5694-48bf-82c1-8780639504b8")
    async def create_rack_role(self, rack_role: schemas.RackRoleCreate) -> IdResponse:
        new_obj = await self.dto.create(self.session, rack_role)
        return IdResponse(id=new_obj.id)

    @router.put("/rack-roles/{id}", operation_id="9ab5b8b1-3134-411c-b792-ba5f1a2cc114")
    async def update_rack_role(self, id: int, rack_role: schemas.RackRoleUpdate) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_obj, rack_role)
        return IdResponse(id=id)

    @router.get("/rack-roles/{id}", operation_id="1e3b906c-b381-4482-929d-d27435c2e49b")
    async def get_rack_role(self, id: int) -> schemas.RackRole:
        db_obj = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.RackRole.model_validate(db_obj)

    @router.get("/rack-roles", operation_id="1fe1c9b0-31a1-41c4-82e5-6f96e1c18113")
    async def get_rack_roles(self, q: schemas.RackRoleQuery = Depends()) -> ListT[schemas.RackRole]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.RackRole.model_validate(r) for r in results])

    @router.delete("/rack-roles/{id}", operation_id="c384b7b7-c266-4d01-976a-1867ed526b5e")
    async def delete_rack_role(self, id: int) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_obj)
        return IdResponse(id=id)

    @router.get("/rack-roles/{id}/auditlogs", operation_id="9583bb25-1898-4500-8c87-aa81c8059525")
    async def get_rack_role_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class IPRoleAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(IPRole)

    @router.post("/ip-roles", operation_id="6adadd9a-f2d9-49da-824f-58df420ab35e")
    async def create_ip_role(self, ip_role: schemas.IPRoleCreate) -> IdResponse:
        new_obj = await self.dto.create(self.session, ip_role)
        return IdResponse(id=new_obj.id)

    @router.put("/ip-roles/{id}", operation_id="b582d431-db75-47fc-840b-0061f3cd1a2c")
    async def update_ip_role(self, id: int, ip_role: schemas.IPRoleUpdate) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_obj, ip_role)
        return IdResponse(id=id)

    @router.get("/ip-roles/{id}", operation_id="e37f0bc5-2e54-4cae-8f8b-bc226f61f862")
    async def get_ip_role(self, id: int) -> schemas.IPRole:
        db_obj = await self.dto.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.IPRole.model_validate(db_obj)

    @router.get("/ip-roles", operation_id="333be12d-5f84-46ca-af12-2790708d9ef9")
    async def get_ip_roles(self, q: schemas.IPRoleQuery = Depends()) -> ListT[schemas.IPRole]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.IPRole.model_validate(r) for r in results])

    @router.delete("/ip-roles/{id}", operation_id="188cb57e-1218-47c8-bd0d-fbe7a3b951ec")
    async def delete_ip_role(self, id: int) -> IdResponse:
        db_obj = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_obj)
        return IdResponse(id=id)

    @router.get("/ip-roles/{id}/auditlogs", operation_id="fff1a675-1652-42e7-9619-f8be929c1ab9")
    async def get_ip_role_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])
