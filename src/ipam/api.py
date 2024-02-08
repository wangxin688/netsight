from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src._types import AuditLog, IdResponse, ListT
from src.cbv import cbv
from src.db import ASN, VLAN, VRF, Block, IPAddress, IPRange, IPRole, Prefix, Site, User
from src.db.dtobase import DtoBase
from src.deps import auth, get_session
from src.ipam import schemas

router = APIRouter()


@cbv(router)
class BlockAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(Block)

    @router.post("/blocks", operation_id="2c7ff1ce-67da-4b95-86b4-b01d3398ba9e")
    async def create_block(self, block: schemas.BlockCreate) -> IdResponse:
        new_block = await self.dto.create(self.session, block)
        return IdResponse(id=new_block.id)

    @router.put("/blocks/{id}", operation_id="9798ef27-8678-4557-ac27-9284db0b9cb0")
    async def update_block(self, id: int, block: schemas.BlockUpdate) -> IdResponse:
        local_block = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, local_block, block)
        return IdResponse(id=id)

    @router.get("/blocks/{id}", operation_id="ceeda791-0ec7-458d-9246-ab688ed40e5a")
    async def get_block(self, id: int) -> schemas.Block:
        local_block = await self.dto.get_one_or_404(self.session, id)
        return schemas.Block.model_validate(local_block)

    @router.get("/blocks", operation_id="7c3c68e7-de01-4b15-9a0c-90fc328a759a")
    async def get_blocks(self, q: schemas.BlockQuery = Depends()) -> ListT[schemas.Block]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.BlockList.model_validate(r) for r in results])

    @router.delete("/blocks/{id}", operation_id="c55f28df-9fe8-4ab7-92c7-aa98de2a53ef")
    async def delete_block(self, id: int) -> IdResponse:
        local_block = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, local_block)
        return IdResponse(id=id)

    @router.get("/blocks/{id}/auditlogs", operation_id="b81b96bf-dd24-4114-b57e-71fc835a0e76")
    async def get_block_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class PrefixAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(Prefix)

    @router.post("/prefixes", operation_id="d808fdd1-096b-400e-af49-8edf6d5db288")
    async def create_prefix(self, prefix: schemas.PrefixCreate) -> IdResponse:
        new_prefix = await self.dto.create(self.session, prefix)
        return IdResponse(id=new_prefix.id)

    @router.put("/prefixes/{id}", operation_id="7770767a-1862-45ea-9352-375e8b83e3a0")
    async def update_prefix(self, id: int, prefix: schemas.PrefixUpdate) -> IdResponse:
        local_prefix = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, local_prefix, prefix)
        return IdResponse(id=id)

    @router.get("/prefixes/{id}", operation_id="7b912ed7-09b6-4537-b4b9-6a79c589e7d9")
    async def get_prefix(self, id: int) -> schemas.Prefix:
        local_prefix = await self.dto.get_one_or_404(
            self.session,
            id,
            selectinload(Prefix.site).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Prefix.vrf).load_only(VRF.id, VRF.name, VRF.rd),
            selectinload(Prefix.role).load_only(IPRole.id, IPRole.name),
            selectinload(Prefix.vlan).load_only(VLAN.id, VLAN.name, VLAN.vid),
        )
        return schemas.Prefix.model_validate(local_prefix)

    @router.get("/prefixes", operation_id="9e8f9325-3aac-4b6f-9585-2abc03e1ed9c")
    async def get_prefixes(self, q: schemas.PrefixQuery = Depends()) -> ListT[schemas.Prefix]:
        count, results = await self.dto.list_and_count(
            self.session,
            q,
            selectinload(Prefix.site).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Prefix.vrf).load_only(VRF.id, VRF.name, VRF.rd),
            selectinload(Prefix.role).load_only(IPRole.id, IPRole.name),
            selectinload(Prefix.vlan).load_only(VLAN.id, VLAN.name, VLAN.vid),
        )
        return ListT(count=count, results=[schemas.PrefixList.model_validate(r) for r in results])

    @router.delete("/prefixes/{id}", operation_id="18c5ce9e-97ce-427c-9cf1-fd5a34f9c9f8")
    async def delete_prefix(self, id: int) -> IdResponse:
        local_prefix = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, local_prefix)
        return IdResponse(id=id)

    @router.get("/prefixes/{id}/auditlogs", operation_id="fcf939e5-99b5-40af-be76-41df06aa4e08")
    async def get_prefix_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class ASNAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(ASN)

    @router.post("/asn", operation_id="6fa6b751-8366-40c3-a5e7-8dcfa0b2e0a4")
    async def create_asn(self, asn: schemas.ASNCreate) -> IdResponse:
        new_asn = await self.dto.create(self.session, asn)
        return IdResponse(id=new_asn.id)

    @router.put("/asn/{id}", operation_id="3713c5f2-868b-49a1-9b74-7fa22d9233de")
    async def update_asn(self, id: int, asn: schemas.ASNUpdate) -> IdResponse:
        local_asn = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, local_asn, asn)
        return IdResponse(id=id)

    @router.get("/asn/{id}", operation_id="9d1deb3d-3ec8-419f-a05a-5f60a39b60e6")
    async def get_asn(self, id: int) -> schemas.ASN:
        local_asn = await self.dto.get_one_or_404(self.session, id)
        return schemas.ASN.model_validate(local_asn)

    @router.get("/asn", operation_id="c90a4645-c1d6-4e6d-afd5-fa89a2e38e5c")
    async def get_asns(self, q: schemas.ASNQuery = Depends()) -> ListT[schemas.ASN]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.ASNList.model_validate(r) for r in results])

    @router.delete("/asn/{id}", operation_id="bea2daf9-5a92-44e6-b52b-5f724f6924da")
    async def delete_asn(self, id: int) -> IdResponse:
        local_asn = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, local_asn)
        return IdResponse(id=id)

    @router.get("/asns/{id}/auditlogs", operation_id="9c70deb7-9d35-4b6b-8cc9-60dc6203dae8")
    async def get_asn_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class IPRangeAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(IPRange)

    @router.post("/ip-ranges", operation_id="9130ab51-bbf2-43ab-a1f5-7b52dbc6aebc")
    async def create_ip_range(self, ip_range: schemas.IPRangeCreate) -> IdResponse:
        new_ip_range = await self.dto.create(self.session, ip_range)
        return IdResponse(id=new_ip_range.id)

    @router.put("/ip-ranges/{id}", operation_id="d223fc14-0b20-46bc-af3c-e57f08c81404")
    async def update_ip_range(self, id: int, ip_range: schemas.IPRangeUpdate) -> IdResponse:
        local_ip_range = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, local_ip_range, ip_range)
        return IdResponse(id=id)

    @router.get("/ip-ranges/{id}", operation_id="6761156d-0328-47d0-8f3d-793ea5e16dd6")
    async def get_ip_range(self, id: int) -> schemas.IPRange:
        local_ip_range = await self.dto.get_one_or_404(self.session, id)
        return schemas.IPRange.model_validate(local_ip_range)

    @router.get("/ip-ranges", operation_id="79b4955b-3253-401e-92cd-2ad41f1306f2")
    async def get_ip_ranges(self, q: schemas.IPRangeQuery = Depends()) -> ListT[schemas.IPRange]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.IPRangeList.model_validate(r) for r in results])

    @router.delete("/ip-ranges/{id}", operation_id="cf398770-377c-4435-b30e-ec019d92c05d")
    async def delete_ip_range(self, id: int) -> IdResponse:
        local_ip_range = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, local_ip_range)
        return IdResponse(id=id)

    @router.get("/ip-ranges/{id}/auditlogs", operation_id="3376d677-ac4b-4748-a31b-4fc0035230ef")
    async def get_ip_range_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class IPAddressAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(IPAddress)

    @router.post("/ip-addresses", operation_id="856265ea-244b-4587-a64d-34cbe51b146e")
    async def create_ip_address(self, ip_address: schemas.IPAddressCreate) -> IdResponse:
        new_ip_address = await self.dto.create(self.session, ip_address)
        return IdResponse(id=new_ip_address.id)

    @router.put("/ip-addresses/{id}", operation_id="3551f799-33c9-43ea-b071-89162c319812")
    async def update_ip_address(self, id: int, ip_address: schemas.IPAddressUpdate) -> IdResponse:
        local_ip_address = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, local_ip_address, ip_address)
        return IdResponse(id=id)

    @router.get("/ip-addresses/{id}", operation_id="4bf79652-8e21-41ff-bbdb-87ad5537506c")
    async def get_ip_address(self, id: int) -> schemas.IPAddress:
        local_ip_address = await self.dto.get_one_or_404(self.session, id)
        return schemas.IPAddress.model_validate(local_ip_address)

    @router.get("/ip-addresses", operation_id="06b038a0-7568-4ace-b090-295dd150afe1")
    async def get_ip_addresses(self, q: schemas.IPAddressQuery = Depends()) -> ListT[schemas.IPAddress]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.IPAddressList.model_validate(r) for r in results])

    @router.delete("/ip-addresses/{id}", operation_id="c2b70972-c9b0-404d-b433-42cedcc812d9")
    async def delete_ip_address(self, id: int) -> IdResponse:
        local_ip_address = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, local_ip_address)
        return IdResponse(id=id)

    @router.get("/ip-addresses/{id}/auditlogs", operation_id="83f8eb5e-385e-4b9c-b969-275fc5229ac1")
    async def get_ip_address_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])


@cbv(router)
class VLANAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = DtoBase(VLAN)

    @router.post("/vlans", operation_id="89b40e79-63fd-48c2-8af9-6a472cb72135")
    async def create_vlan(self, vlan: schemas.VLANCreate) -> IdResponse:
        new_vlan = await self.dto.create(self.session, vlan)
        return IdResponse(id=new_vlan.id)

    @router.put("/vlans/{id}", operation_id="fef06094-f1dc-416b-8b99-497f8ecd3fde")
    async def update_vlan(self, id: int, vlan: schemas.VLANUpdate) -> IdResponse:
        local_vlan = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, local_vlan, vlan)
        return IdResponse(id=id)

    @router.get("/vlans/{id}", operation_id="1dc5abd9-e591-418d-bc64-440e1b406ccf")
    async def get_vlan(self, id: int) -> schemas.VLAN:
        local_vlan = await self.dto.get_one_or_404(self.session, id)
        return schemas.VLAN.model_validate(local_vlan)

    @router.get("/vlans", operation_id="0e713497-6230-4cdb-bfdd-1b3016664c61")
    async def get_vlans(self, q: schemas.VLANQuery = Depends()) -> ListT[schemas.VLAN]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.VLANList.model_validate(r) for r in results])

    @router.delete("/vlans/{id}", operation_id="b2878bc9-500f-4990-84b4-f67faed952ae")
    async def delete_vlan(self, id: int) -> IdResponse:
        local_vlan = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, local_vlan)
        return IdResponse(id=id)

    @router.get("/vlans/{id}/auditlogs", operation_id="d5138fed-4af4-4e81-a002-324b7c3e1050")
    async def get_vlan_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.dto.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])
