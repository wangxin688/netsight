from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.models import User
from src.api.base import BaseListResponse, BaseResponse, QueryParams
from src.api.deps import get_current_user, get_session
from src.api.ipam import schemas
from src.api.ipam.models import ASN, RIR, Block, IPRole
from src.db.crud_base import CRUDBase
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_4004, ERR_NUM_4009, ResponseMsg

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class RIRCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(RIR)

    @router.post("/rirs")
    async def create_rir(self, rir: schemas.RIRCreate) -> BaseResponse[int]:
        local_rir = await self.crud.get_by_field(self.session, "name", rir.name)
        if local_rir:
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Create RIR failed, rir with name {rir.name} already existed"
            )
            return return_info
        new_rir = RIR(**rir.dict())
        self.session.add(new_rir)
        await self.session.commit()
        return_info = ResponseMsg(data=new_rir.id)
        return return_info

    @router.get("/rirs/{id}")
    async def get_rir(self, id: int) -> BaseResponse[schemas.RIR]:
        local_rir: RIR = await self.session.get(RIR, id)
        if not local_rir:
            return_info = ERR_NUM_4004
            return_info.msg = f"RIR #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_rir)
        return return_info

    @router.get("/rirs")
    async def get_rirs(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.RIR]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(select(func.count(RIR.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.put("/rirs/{id}")
    async def update_rir(self, id: int, rir: schemas.RIRUpdate) -> BaseResponse[int]:
        local_rir: RIR = await self.session.get(RIR, id)
        if not local_rir:
            return_info = ERR_NUM_4004
            return_info.msg = f"Update rir failed, rir #{id} not found"
            return return_info
        try:
            await self.crud.update(self.session, id, rir)
        except IntegrityError as e:
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Update rir failed, rir with same name {rir.name} already existed"
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/rirs/{id}")
    async def delete_rir(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete rir failed, rir #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/rirs/deleteList")
    async def delete_rirs(self, rir: schemas.RIRBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, rir.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk delete rirs failed, rir with #{rir.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results])
        return return_info


@cbv(router)
class ASNCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(ASN)

    @router.post("/asns")
    async def create_asn(self, asn: schemas.ASNCreate) -> BaseResponse[int]:
        local_asn = await self.crud.get_by_field(self.session, "asn", asn.asn)
        if local_asn:
            return_info = ERR_NUM_4009
            return_info.msg = f"Create asn failed, asn #{asn.asn} already existed"
            return return_info
        new_asn = ASN(**asn.dict())
        self.session.add(new_asn)
        await self.session.commit()
        return_info = ResponseMsg(data=new_asn.id)
        return return_info

    @router.get("/asns/{id}")
    async def get_asn(self, id: int) -> BaseResponse[schemas.ASN]:
        local_asn: ASN = await self.session.get(ASN, id)
        if not local_asn:
            return_info = ERR_NUM_4004
            return_info.msg = f"ASN #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_asn)
        return return_info

    @router.get("/asns")
    async def get_asns(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.ASN]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(select(func.count(ASN.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.put("/asns/{id]")
    async def update_asn(self, id: int, asn: schemas.ASNUpdate) -> BaseResponse[int]:
        local_asn: ASN = await self.session.get(ASN, id)
        if not local_asn:
            return_info = ERR_NUM_4004
            return_info.msg = f"Update asn failed, asn #{id} not found"
            return return_info
        try:
            await self.crud.update(self.session, id, asn)
        except IntegrityError as e:
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = f"Update asn failed, asn #{asn.asn} already existed"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/asns/{id}")
    async def delete_asn(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info = f"Delete asn failed, asn #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/asns/deleteList")
    async def delete_asns(self, asn: schemas.ASNBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, asn.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk delete asns failed, asn #{asn.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results])
        return return_info


@cbv(router)
class BlockCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Block)

    @router.post("/blocks")
    async def create_block(self, block: schemas.BlockCreate) -> BaseResponse[int]:
        rir: RIR = self.session.get(RIR, id)
        if not rir:
            return_info = ERR_NUM_4004
            return_info.msg = f"Create block failed, block with rir #{id} not found"
            return return_info

        new_block = Block(**block.dict())
        self.session.add(new_block)
        await self.session.commit()
        return_info = ResponseMsg(data=new_block.id)
        return return_info

    @router.get("/blocks/{id}")
    async def get_block(self, id: int) -> BaseResponse[schemas.Block]:
        local_block: Block = await self.session.get(Block, id)
        if not local_block:
            return_info = ERR_NUM_4004
            return_info.msg = "Block #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_block)
        return return_info

    @router.get("/blocks")
    async def get_blocks(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.Block]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(select(func.count(Block.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.put("/blocks/{id}")
    async def update_block(self, block: schemas.BlockUpdate) -> BaseResponse[int]:
        local_block: Block = await self.session.get(Block, id)
        if not local_block:
            return_info = ERR_NUM_4004
            return_info.msg = f"Update block failed, block #{id} not found"
            return return_info
        if block.rir_id:
            local_rir: RIR = await self.session.get(RIR, id)
            if not local_rir:
                return_info = ERR_NUM_4004
                return_info.msg = f"Update block failed, block with rir #{id} not found"
                return return_info
        await self.crud.update(self.session, id, block)
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/blocks/{id}")
    async def delete_block(self, id) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete block failed, block #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/blocks/deleteList")
    async def delete_blocks(self, block: schemas.Block) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, block.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = f"Bulk delete blocks failed, block #{block.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results])
        return return_info


@cbv(router)
class IPRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(IPRole)

    @router.post("/roles")
    async def create_ipam_role(self, role: schemas.IPRoleCreate) -> BaseResponse[int]:
        local_role = await self.crud.get_by_field(self.session, "name", role.name)
        if local_role:
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Create IP role failed, role with name {role.name} already existed"
            )
            return return_info
        new_role = IPRole(**role.dict())
        self.session.add(new_role)
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.get("/roles/{id}")
    async def get_ipam_role(self, id: int) -> BaseResponse[schemas.IPRole]:
        local_role: IPRole = await self.session.get(self.session, id)
        if not local_role:
            return_info = ERR_NUM_4004
            return_info.msg = f"IP role #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_role)
        return return_info

    @router.get("/roles")
    async def get_ipam_roles(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.IPRole]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (
            await self.session.execute(select(func.count(IPRole.id)))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.update("/roles/{id}")
    async def update_ipam_role(
        self, id: int, role: schemas.IPRoleUpdate
    ) -> BaseResponse[int]:
        local_role: IPRole = await self.session.get(IPRole, id)
        if not local_role:
            return_info = ERR_NUM_4004
            return_info.msg = f"Update IP role failed, ip role #{id} not found"
            return return_info
        try:
            await self.crud.update(self.session, id, role)
        except IntegrityError as e:
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Update IP role failed, ip role with name {role.name} already exsited"
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/roles/{id}")
    async def delete_ipam_role(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete ip role failed, ip role #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/roles/deleteList")
    async def delete_ipam_roles(
        self, role: schemas.IPRoleBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, role.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Bulk delete IP roles failed, ip role #{role.ids} not found"
            )
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results])
        return return_info
