from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.repositories import BaseRepository
from src.core.utils.cbv import cbv
from src.features._types import AuditLog, IdResponse, ListT
from src.features.admin.models import User
from src.features.arch.models import CircuitType
from src.features.circuit import schemas
from src.features.circuit.models import ISP, Circuit
from src.features.circuit.services import CircuitDto
from src.features.dcim.models import Device, Interface
from src.features.deps import auth, get_session
from src.features.ipam.models import ASN
from src.features.org.models import Site

router = APIRouter()


class IspAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = BaseRepository(ISP)

    @router.post("/isp", operation_id="1cbcccdd-10f3-4d7c-80c9-64b1dccdbe18")
    async def create_isp(self, isp: schemas.ISPCreate) -> IdResponse:
        new_isp = await self.dto.create(self.session, isp)
        return IdResponse(id=new_isp.id)

    @router.put("/isp/{id}", operation_id="534e2c63-5fdf-494b-a73b-083d5316f646")
    async def update_isp(self, id: int, isp: schemas.ISPUpdate) -> IdResponse:
        db_isp = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_isp, isp)
        return IdResponse(id=id)

    @router.get("/isp/{id}", operation_id="9c132285-b785-41b9-b3c9-9d13320dcd1a")
    async def get_isp(self, id: int) -> schemas.ISP:
        db_isp = await self.dto.get_one_or_404(self.session, id, selectinload(ISP.asn).load_only(ASN.id, ASN.asn))
        return schemas.ISP.model_validate(db_isp)

    @router.get("/isps", operation_id="a0f9b45c-868a-4b55-9632-977648011e35")
    async def get_isps(self, q: schemas.ISPQuery = Depends()) -> ListT[schemas.ISPList]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.ISPList.model_validate(r) for r in results])

    @router.delete("/isp/{id}", operation_id="45e468e9-c04c-4d13-999c-36c48265fe0d")
    async def delete_isp(self, id: int) -> IdResponse:
        db_isp = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_isp)
        return IdResponse(id=id)

    @router.get("/isp/{id}/auditlogs", operation_id="e926c14a-560e-416f-886d-7a4396b89da8")
    async def get_isp_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class CircuitAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = CircuitDto(Circuit)

    @router.post("/circuits", operation_id="f194c1b6-8a13-4759-aad5-8c2e4e24757a")
    async def create_circuit(self, circuit: schemas.CircuitCreate) -> IdResponse:
        site_a_id, device_a_id = await self.dto.get_interface_info(self.session, circuit.interface_a_id)
        new_circuit = await self.dto.create(self.session, circuit, commit=False)
        new_circuit.site_a_id = site_a_id
        new_circuit.device_a_id = device_a_id
        if circuit.interface_z_id:
            site_z_id, device_z_id = await self.dto.get_interface_info(self.session, circuit.interface_z_id)
            new_circuit.site_z_id = site_z_id
            new_circuit.device_z_id = device_z_id
        new_circuit = await self.dto.commit(self.session, new_circuit)
        return IdResponse(id=new_circuit.id)

    @router.put("/circuits/{id}", operation_id="c35fb93d-6e66-4bc9-afc7-25eb098da1ce")
    async def update_circuit(self, id: int, circuit: schemas.CircuitUpdate) -> IdResponse:
        db_circuit = await self.dto.get_one_or_404(self.session, id)
        if circuit.interface_z_id:
            site_z_id, device_z_id = await self.dto.get_interface_info(self.session, circuit.interface_z_id)
            db_circuit.site_z_id = site_z_id
            db_circuit.device_z_id = device_z_id
        if circuit.interface_a_id:
            site_a_id, device_a_id = await self.dto.get_interface_info(self.session, circuit.interface_a_id)
            db_circuit.site_a_id = site_a_id
            db_circuit.device_a_id = device_a_id
        await self.dto.update(self.session, db_circuit, circuit, excludes={"interface_a_id", "interface_z_id"})
        return IdResponse(id=id)

    @router.get("/circuits/{id}", operation_id="bf09c339-0fbd-4150-84c1-817a0e49d896")
    async def get_circuit(self, id: int) -> schemas.Circuit:
        db_circuit = await self.dto.get_one_or_404(
            self.session,
            id,
            selectinload(Circuit.circuit_type).load_only(CircuitType.id, CircuitType.name),
            selectinload(Circuit.isp).load_only(ISP.id, ISP.name),
            selectinload(Circuit.site_a).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Circuit.device_a).load_only(
                Device.id, Device.name, Device.management_ipv4, Device.management_ipv6
            ),
            selectinload(Circuit.interface_a).load_only(Interface.id, Interface.name),
            selectinload(Circuit.site_z).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Circuit.device_z).load_only(
                Device.id, Device.name, Device.management_ipv4, Device.management_ipv6
            ),
            selectinload(Circuit.interface_z).load_only(Interface.id, Interface.name),
        )
        return schemas.Circuit.model_validate(db_circuit)

    @router.get("/circuits", operation_id="6eb35cf7-ec59-4bb3-8a6d-dd1d07375aca")
    async def get_circuits(self, q: schemas.CircuitQuery = Depends()) -> ListT[schemas.Circuit]:
        count, results = await self.dto.list_and_count(
            self.session,
            q,
            selectinload(Circuit.circuit_type).load_only(CircuitType.id, CircuitType.name),
            selectinload(Circuit.isp).load_only(ISP.id, ISP.name),
            selectinload(Circuit.site_a).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Circuit.device_a).load_only(
                Device.id, Device.name, Device.management_ipv4, Device.management_ipv6
            ),
            selectinload(Circuit.interface_a).load_only(Interface.id, Interface.name),
            selectinload(Circuit.site_z).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Circuit.device_z).load_only(
                Device.id, Device.name, Device.management_ipv4, Device.management_ipv6
            ),
            selectinload(Circuit.interface_z).load_only(Interface.id, Interface.name),
        )
        return ListT(count=count, results=[schemas.Circuit.model_validate(r) for r in results])

    @router.delete("/circuits/{id}", operation_id="58ff4f23-f533-4eb7-bfa4-2c97d6e4be17")
    async def delete_circuit(self, id: int) -> IdResponse:
        db_circuit = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_circuit)
        return IdResponse(id=id)

    @router.get("/circuits/{id}/auditlogs", operation_id="71070890-5afc-4609-b4fe-c76dfd0fe701")
    async def get_circuit_audit_logs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])
