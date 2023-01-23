from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.models import User
from src.app.base import BaseListResponse, BaseResponse, QueryParams
from src.app.dcim.models import Site
from src.app.deps import get_current_user, get_session
from src.app.ipam import schemas
from src.app.ipam.models import (
    ASN,
    RIR,
    VLAN,
    VRF,
    Block,
    IPRange,
    IPRole,
    Prefix,
    VLANGroup,
)
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

    @router.put("/roles/{id}")
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


class PrefixCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Prefix)

    @router.post("/prefixes")
    async def create_prefix(self, prefix: schemas.PrefixCreate) -> BaseResponse[int]:
        return_info = ERR_NUM_4004
        site: Site = await self.session.get(Site, prefix.site_id)
        if not site:
            return_info.msg = f"Create prefix failed, site #{prefix.site_id} not found"
            return return_info
        ipam_role: IPRole = await self.session.get(IPRole, prefix.role_id)
        if not ipam_role:
            return_info.msg = f"Create prefix failed, role #{id} not found"
            return return_info
        new_prefix = Prefix(**prefix.dict())
        self.session.add(prefix)
        await self.session.commit()
        return_info = ResponseMsg(data=new_prefix.id)
        return return_info

    @router.get("/prefixes/{id}")
    async def get_prefix(self, id: int) -> BaseResponse[schemas.Prefix]:
        local_prefix: Prefix = await self.session.get(Prefix, id)
        if not local_prefix:
            return_info = ERR_NUM_4004
            return_info.msg = f"Prefix #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_prefix)
        return return_info

    @router.get("/prefixes")
    async def get_prefixes(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.Prefix]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (
            await self.session.execute(select(func.count(Prefix.id)))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/prefixes/getList")
    async def get_prefix_filter(
        self, prefix: schemas.PrefixQuery
    ) -> BaseListResponse[List[schemas.Prefix]]:
        pass

    @router.put("/prefixes/{id}")
    async def update_prefix(
        self, id: int, prefix: schemas.PrefixUpdate
    ) -> BaseResponse[int]:
        return_info = ERR_NUM_4004
        local_prefix: Prefix = await self.session.get(Prefix, id)
        if not local_prefix:
            return_info.msg = f"Prefix update failed, prefix #{id} not found"
            return return_info
        if prefix.site_id:
            site: Site = await self.session.get(Site, prefix.site_id)
            if not site:
                return_info.msg = (
                    f"Update prefix failed, site #{prefix.site_id} not found"
                )
                return return_info
        if prefix.role_id:
            ipam_role: IPRole = await self.session.get(IPRole, prefix.role_id)
            if not ipam_role:
                return_info.msg = f"Update prefix failed, role #{id} not found"
                return return_info
        await self.crud.update(self.session, id, prefix)
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/prefixes/updateList")
    async def update_prefixes(
        self, prefix: schemas.PrefixBulkUpdate
    ) -> BaseResponse[List[int]]:
        results = await self.crud.get_multi(self.session, prefix.ids)
        return_info = ERR_NUM_4004
        if not results:
            return_info.msg = f"Update prefix failed, prefix #{prefix.ids} not found"
            return return_info
        if len(results) < len(set(prefix.ids)):
            diff_ids = set(prefix.ids) - set([result.id for result in results])
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Update prefix failed, prefix #{list(diff_ids)} not found"
            )
            return return_info
        await self.crud.update_multi(
            self.session,
            prefix.ids,
            prefix,
            excludes={
                "ids",
            },
        )
        return_info = ResponseMsg(data=prefix.ids)
        return return_info

    @router.delete("/prefixes/{id}")
    async def delete_prefix(self, id: int):
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete prefix failed, prefix #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/prefixes/deleteList")
    async def delete_prefixes(self, prefix: schemas.PrefixBulkDelete):
        results = await self.crud.delete_multi(self.session, prefix.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Delete prefixes failed, prefixes #{prefix.ids} not found"
            )
            return return_info
        return_info = ResponseMsg(data=prefix.ids)
        return return_info


@cbv(router)
class VLANGroupCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(VLANGroup)

    @router.post("/vlan-groups")
    async def create_vlan_group(
        self, vlan_group: schemas.VLANGroupCreate
    ) -> BaseResponse[int]:
        local_vlan_group = await self.crud.get_by_field(
            self.session, "name", vlan_group.name
        )
        if local_vlan_group:
            return_info = ERR_NUM_4009
            return_info.msg = f"Create vlan group failed, vlan group with name `{vlan_group.name}` already exists"
            return return_info
        new_vlan_group = VLANGroup(**vlan_group.dict())
        self.session.add(new_vlan_group)
        await self.session.commit()
        return_info = ResponseMsg(data=new_vlan_group.id)
        return return_info

    @router.get("/vlan-groups/{id}")
    async def get_vlan_group(self, id: int) -> BaseResponse[schemas.VLANGroup]:
        local_vlan_group: VLANGroup = await self.session.get(VLANGroup, id)
        if not local_vlan_group:
            return_info = ERR_NUM_4004
            return_info.msg = f"VLAN group #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_vlan_group)
        return return_info

    @router.get("/vlan-groups")
    async def get_vlan_groups(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.VLANGroup]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (
            await self.session.execute(select(func.count(VLANGroup.id)))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/vlan-groups/getList")
    async def get_vlan_group_filter(
        self, vlan_group: schemas.VLANGroupQuery
    ) -> BaseListResponse[List[schemas.VLANGroup]]:
        pass

    @router.put("/vlan-groups/{id}")
    async def update_vlan_group(
        self, id: int, vlan_group: schemas.VLANGroupUpdate
    ) -> BaseResponse[int]:
        local_vlan_group: VLANGroup = await self.session.get(VLANGroup, id)
        if not local_vlan_group:
            return_info = ERR_NUM_4004
            return_info.msg = f"Update vlan group failed, vlan group #{id} not found"
            return return_info
        try:
            await self.crud.update(self.session, id, vlan_group)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = f"Update vlan group failed, vlan group with name {vlan_group.name} already exists"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/vlan-groups/{id}")
    async def delete_vlan_group(self, id) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete vlan group failed, vlan group #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/vlan-groups/deleteList")
    async def delete_vlan_groups(self, vlan_group: schemas.VLANGroupBulkDelete):
        results = await self.crud.delete_multi(self.session, vlan_group.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Delete vlan groups failed, vlan groups #{vlan_group.ids} not found"
            )
            return return_info
        return_info = ResponseMsg(data=vlan_group.ids)
        return return_info


@cbv(router)
class VLANCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(VLAN)

    @router.post("/vlans")
    async def create_vlan(self, vlan: schemas.VLANCreate) -> BaseResponse[int]:
        return_info = ERR_NUM_4004
        if vlan.site_id:
            site: Site = await self.session.get(VLAN, vlan.site_id)
            if not site:
                return_info.msg = f"Create VLAN failed, site #{vlan.site_id} not found"
                return return_info
        if vlan.role_id:
            role: IPRole = await self.session.get(VLAN, vlan.role_id)
            if not role:
                return_info.msg = (
                    f"Create VLAN failed, ip role #{vlan.role_id} not found"
                )
                return return_info
        new_vlan = VLAN(**vlan.dict())
        try:
            self.session.add(new_vlan)
            await self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Create VLAN failed, vlan id #{vlan.vlan_id} already exists"
            )
            return return_info
        return_info = ResponseMsg(data=new_vlan.id)
        return return_info

    @router.get("/vlans/{id}")
    async def get_vlan(self, id: int) -> BaseResponse[schemas.VLAN]:
        local_vlan: VLAN = await self.session.get(VLAN, id)
        if not local_vlan:
            return_info = ERR_NUM_4004
            return_info.msg = f"VLAN #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_vlan)
        return return_info

    @router.get("/vlans")
    async def get_vlans(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.VLAN]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(select(func.count(VLAN.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/vlans/getList")
    async def get_vlans_filter(
        self, vlan: schemas.VLANQuery
    ) -> BaseListResponse[List[schemas.VLAN]]:
        pass

    @router.put("/vlans/{id}")
    async def update_vlan(self, id: int, vlan: schemas.VLANUpdate) -> BaseResponse[int]:
        return_info = ERR_NUM_4004
        if vlan.site_id:
            site: Site = await self.session.get(VLAN, vlan.site_id)
            if not site:
                return_info.msg = f"Update VLAN failed, site #{vlan.site_id} not found"
                return return_info
        if vlan.role_id:
            role: IPRole = await self.session.get(VLAN, vlan.role_id)
            if not role:
                return_info.msg = (
                    f"Update VLAN failed, ip role #{vlan.role_id} not found"
                )
                return return_info
        try:
            await self.crud.update(self.session, id, vlan)
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            return_info = ERR_NUM_4009
            return_info.msg = (
                f"Update VLAN failed, vlan id #{vlan.vlan_id} already exists"
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/vlans/updateList")
    async def update_vlans(
        self, vlan: schemas.VLANBulkUpdate
    ) -> BaseResponse[List[int]]:
        results = await self.crud.get_multi(self.session, vlan.ids)
        return_info = ERR_NUM_4004
        if not results:
            return_info.msg = f"Update VLAN failed, vlan id #{vlan.ids} not found"
        if len(results) < set(vlan.ids):
            diff_ids = set(vlan.ids) - set([result.id for result in results])
            return_info.msg = f"Update VLAN failed, vlan id #{list(diff_ids)} not found"
            return return_info
        if vlan.site_id:
            site: Site = await self.session.get(VLAN, vlan.site_id)
            if not site:
                return_info.msg = f"Update VLAN failed, site #{vlan.site_id} not found"
                return return_info
        if vlan.role_id:
            role: IPRole = await self.session.get(VLAN, vlan.role_id)
            if not role:
                return_info.msg = (
                    f"Update VLAN failed, ip role #{vlan.role_id} not found"
                )
                return return_info
        await self.crud.update_multi(self.session, vlan.ids, vlan, excludes={"ids"})
        return_info = ResponseMsg(data=vlan.ids)
        return return_info

    @router.delete("/vlans/{id}")
    async def delete_vlan(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            result_info = ERR_NUM_4004
            result_info.msg = f"Delete VLAN failed, vlan #{id} not found"
            return result_info
        result_info = ResponseMsg(data=id)
        return result_info

    @router.post("/vlans/deleteList")
    async def delete_vlans(
        self, vlan: schemas.VLANBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, vlan.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete VLAN failed, vlan #{vlan.ids} not found"
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results])
        return return_info


@cbv(router)
class IPRangeCVB:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(IPRange)

    @router.post("/ip-ranges")
    async def create_ip_range(
        self, ip_range: schemas.IPRangeCreate
    ) -> BaseResponse[int]:
        return_info = ERR_NUM_4004
        if ip_range.vrf_id:
            vrf: VRF = await self.session.get(VRF, id)
            if not vrf:
                return_info.msg = (
                    f"Create ip range failed, vrf #{ip_range.vrf_id} not found"
                )
                return return_info
        if ip_range.role_id:
            role: IPRole = await self.session.get(IPRole, id)
            if not role:
                return_info.msg = (
                    f"Create ip range failed, role #{ip_range.role_id} not found"
                )
                return return_info
        new_ip_range = IPRange(**ip_range.dict())
        self.session.add(new_ip_range)
        await self.session.commit()
        return_info = ResponseMsg(data=new_ip_range.id)
        return return_info

    @router.get("/ip-ranges/{id}")
    async def get_ip_range(self, id: int) -> BaseResponse[schemas.IPRange]:
        result: IPRange = await self.session.get(IPRange, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"IP range #{id} not found"
            return return_info
        return_info = ResponseMsg(data=result)
        return return_info

    @router.get("/ip-ranges")
    async def get_ip_ranges(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.IPRange]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (
            await self.session.execute(select(func.count(IPRange.id)))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/ip-ranges/getList")
    async def get_ip_ranges_filter(
        self, ip_range: schemas.IPRangeQuery
    ) -> BaseListResponse[List[BaseResponse]]:
        pass

    @router.put("/ip-ranges/{id}")
    async def update_ip_range(
        self, ip_range: schemas.IPRangeUpdate
    ) -> BaseResponse[int]:
        local_ip_range: IPRange = await self.session.get(IPRange, id)
        return_info = ERR_NUM_4004
        if not local_ip_range:
            return_info.msg = f"Update ip range failed, ip range #{id} not found"
            return return_info
        if ip_range.role_id:
            ip_role: IPRole = await self.session.get(IPRole, id)
            if not ip_role:
                return_info.msg = f"Update ip range failed, ip role #{id} not found"
                return return_info
        if ip_range.vrf_id:
            vrf: VRF = await self.session.get(VRF, id)
            if not vrf:
                return_info.msg = f"Update ip range failed, vrf #{id} not found"
                return return_info
        await self.crud.update(self.session, id, ip_range)
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/ip-ranges/updateList")
    async def update_ip_ranges(self):
        pass

    @router.delete("/ip-ranges/{id}")
    async def delete_ip_range(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete ip range failed, ip range #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/ip-ranges/deleteList")
    async def delete_ip_ranges(
        self, ip_range: schemas.IPRangeBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, ip_range.ids)
        return_info = ResponseMsg([result.id for result in results])
        return return_info


@cbv(router)
class IPAddressCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(IPRange)

    @router.post("/ip-addresses")
    async def create_ip_address(self, ip_address: schemas.IPAddressCreate)->BaseResponse[int]:
        pass

    @router.get("ip-addresses/{id}")
    async def get_ip_address(self, id: int)->BaseResponse[schemas.IPAddress]:
        pass

    @router.get("/ip-addresses")
    async def get_ip_addresses(self, q: schemas.IPAddress)