from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.models import User
from src.app.base import BaseListResponse, BaseResponse, QueryParams
from src.app.dcim.models import Site
from src.app.deps import get_current_user, get_locale, get_session
from src.app.ipam import schemas
from src.app.ipam.models import ASN, RIR, VLAN, VRF, Block, IPRange, IPRole, Prefix, VLANGroup
from src.db.crud_base import CRUDBase
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_404, ERR_NUM_409, ResponseMsg, error_404_409

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class RIRCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(RIR)
    locale = Depends(get_locale)

    @router.post("/rirs")
    async def create_rir(self, rir: schemas.RIRCreate) -> BaseResponse[int]:
        exist_name = await self.crud.get_by_field(self.session, "name", rir.name)
        if exist_name:
            return_info = error_404_409(ERR_NUM_409, self.locale, "rir", "name", rir.name)
            return return_info
        new_rir = await self.crud.create(self.session, rir)
        return_info = ResponseMsg(data=new_rir.id)
        return return_info

    @router.get("/rirs/{id}")
    async def get_rir(self, id: int) -> BaseResponse[schemas.RIR]:
        local_rir: RIR = await self.session.get(RIR, id)
        if not local_rir:
            return_info = error_404_409(ERR_NUM_404, self.locale, "rir", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_rir, locale=self.locale)
        return return_info

    @router.get("/rirs")
    async def get_rirs(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.RIR]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.put("/rirs/{id}")
    async def update_rir(self, id: int, rir: schemas.RIRUpdate) -> BaseResponse[int]:
        local_rir: RIR = await self.session.get(RIR, id)
        if not local_rir:
            return_info = error_404_409(ERR_NUM_404, self.locale, "rir", "#id", id)
            return return_info
        if rir.name:
            exist_name = await self.crud.get_by_field(self.session, "name", rir.name)
            if exist_name:
                return_info = error_404_409(ERR_NUM_409, self.locale, "rir", "name", rir.name)
                return return_info
        await self.crud.update(self.session, id, rir)
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/rirs/{id}")
    async def delete_rir(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "rir", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/rirs/deleteList")
    async def delete_rirs(self, rir: schemas.RIRBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, rir.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "rir", "#ids", rir.ids)
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results], locale=self.locale)
        return return_info


@cbv(router)
class ASNCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(ASN)
    locale = Depends(get_locale)

    @router.post("/asns")
    async def create_asn(self, asn: schemas.ASNCreate) -> BaseResponse[int]:
        local_asn = await self.crud.get_by_field(self.session, "asn", asn.asn)
        if local_asn:
            return_info = error_404_409(ERR_NUM_409, self.locale, "ASN", "asn", asn.asn)
            return return_info
        new_asn = await self.crud.create(self.session, asn)
        return_info = ResponseMsg(data=new_asn.id, locale=self.locale)
        return return_info

    @router.get("/asns/{id}")
    async def get_asn(self, id: int) -> BaseResponse[schemas.ASN]:
        local_asn: ASN = await self.session.get(ASN, id)
        if not local_asn:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ASN", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_asn, locale=self.locale)
        return return_info

    @router.get("/asns")
    async def get_asns(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.ASN]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.put("/asns/{id]")
    async def update_asn(self, id: int, asn: schemas.ASNUpdate) -> BaseResponse[int]:
        local_asn: ASN = await self.session.get(ASN, id)
        if not local_asn:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ASN", "#id", id)
            return return_info
        exist_num = await self.crud.get_by_field(self.session, "asn", asn.asn)
        if exist_num:
            return_info = error_404_409(ERR_NUM_409, self.locale, "ASN", "asn", asn.asn)
            return return_info

        await self.crud.update(self.session, id, asn)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/asns/{id}")
    async def delete_asn(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ASN", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/asns/deleteList")
    async def delete_asns(self, asn: schemas.ASNBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, asn.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ASN", "#ids", asn.ids)
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results], locale=self.locale)
        return return_info


@cbv(router)
class BlockCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Block)
    locale = Depends(get_locale)

    @router.post("/blocks")
    async def create_block(self, block: schemas.BlockCreate) -> BaseResponse[int]:
        rir: RIR = self.session.get(RIR, block.rir_id)
        if not rir:
            return_info = error_404_409(ERR_NUM_404, self.locale, "rir", "#id", block.rir_id)
            return return_info

        new_block = await self.crud.create(self.session, block)
        return_info = ResponseMsg(data=new_block.id, locale=self.locale)
        return return_info

    @router.get("/blocks/{id}")
    async def get_block(self, id: int) -> BaseResponse[schemas.Block]:
        local_block: Block = await self.session.get(Block, id)
        if not local_block:
            return_info = error_404_409(ERR_NUM_404, self.locale, "block", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_block, locale=self.locale)
        return return_info

    @router.get("/blocks")
    async def get_blocks(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.Block]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.put("/blocks/{id}")
    async def update_block(self, block: schemas.BlockUpdate) -> BaseResponse[int]:
        local_block: Block = await self.session.get(Block, id)
        if not local_block:
            return_info = error_404_409(ERR_NUM_404, self.locale, "block", "#id", id)
            return return_info
        if block.rir_id:
            local_rir: RIR = await self.session.get(RIR, id)
            if not local_rir:
                return_info = error_404_409(ERR_NUM_404, self.locale, "rir", "#id", id)
            return return_info
        await self.crud.update(self.session, id, block)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/blocks/{id}")
    async def delete_block(self, id) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "block", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/blocks/deleteList")
    async def delete_blocks(self, block: schemas.Block) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, block.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ASN", "#ids", block.ids)
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results], locale=self.locale)
        return return_info


@cbv(router)
class IPRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(IPRole)
    locale = Depends(get_locale)

    @router.post("/roles")
    async def create_ip_role(self, role: schemas.IPRoleCreate) -> BaseResponse[int]:
        local_role = await self.crud.get_by_field(self.session, "name", role.name)
        if local_role:
            return_info = error_404_409(ERR_NUM_409, self.locale, "ip-role", "name", role.name)
            return return_info
        new_role = await self.crud.create(self.session, role)
        return_info = ResponseMsg(data=new_role.id, locale=self.locale)
        return return_info

    @router.get("/roles/{id}")
    async def get_ip_role(self, id: int) -> BaseResponse[schemas.IPRole]:
        local_role: IPRole = await self.session.get(self.session, id)
        if not local_role:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_role, locale=self.locale)
        return return_info

    @router.get("/roles")
    async def get_ip_roles(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.IPRole]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.put("/roles/{id}")
    async def update_ip_role(self, id: int, role: schemas.IPRoleUpdate) -> BaseResponse[int]:
        local_role: IPRole = await self.session.get(IPRole, id)
        if not local_role:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
            return return_info
        exist_name = await self.crud.get_by_field(self.session, "name", role.name)
        if exist_name:
            return_info = error_404_409(ERR_NUM_409, self.locale, "ip-role", "name", role.name)
            return return_info
        await self.crud.update(self.session, id, role)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/roles/{id}")
    async def delete_ip_role(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/roles/deleteList")
    async def delete_ip_roles(self, role: schemas.IPRoleBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, role.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#ids", role.ids)
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results], locale=self.locale)
        return return_info


class PrefixCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Prefix)
    locale = Depends(get_locale)

    @router.post("/prefixes")
    async def create_prefix(self, prefix: schemas.PrefixCreate) -> BaseResponse[int]:
        site: Site = await self.session.get(Site, prefix.site_id)
        if not site:
            return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        ipam_role: IPRole = await self.session.get(IPRole, prefix.role_id)
        if not ipam_role:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
            return return_info
        new_prefix = await self.crud.create(self.session, prefix)
        return_info = ResponseMsg(data=new_prefix.id, locale=self.locale)
        return return_info

    @router.get("/prefixes/{id}")
    async def get_prefix(self, id: int) -> BaseResponse[schemas.Prefix]:
        local_prefix: Prefix = await self.session.get(Prefix, id)
        if not local_prefix:
            return_info = error_404_409(ERR_NUM_404, self.locale, "prefix", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_prefix, locale=self.locale)
        return return_info

    @router.get("/prefixes")
    async def get_prefixes(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.Prefix]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.post("/prefixes/getList")
    async def get_prefix_filter(self, prefix: schemas.PrefixQuery) -> BaseListResponse[List[schemas.Prefix]]:
        pass

    @router.put("/prefixes/{id}")
    async def update_prefix(self, id: int, prefix: schemas.PrefixUpdate) -> BaseResponse[int]:
        local_prefix: Prefix = await self.session.get(Prefix, id)
        if not local_prefix:
            return_info = error_404_409(ERR_NUM_404, self.locale, "prefix", "#id", id)
            return return_info
        if prefix.site_id:
            site: Site = await self.session.get(Site, prefix.site_id)
            if not site:
                return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
            return return_info
        if prefix.role_id:
            ip_role: IPRole = await self.session.get(IPRole, prefix.role_id)
            if not ip_role:
                return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
                return return_info
        await self.crud.update(self.session, id, prefix)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/prefixes/updateList")
    async def update_prefixes(self, prefix: schemas.PrefixBulkUpdate) -> BaseResponse[List[int]]:
        results = await self.crud.get_multi(self.session, prefix.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "prefix", "#ids", prefix.ids)
            return return_info
        if len(results) < len(set(prefix.ids)):
            diff_ids = set(prefix.ids) - set([result.id for result in results])
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", list(diff_ids))
            return return_info
        await self.crud.update_multi(
            self.session,
            prefix.ids,
            prefix,
            excludes={
                "ids",
            },
        )
        return_info = ResponseMsg(data=prefix.ids, locale=self.locale)
        return return_info

    @router.delete("/prefixes/{id}")
    async def delete_prefix(self, id: int):
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "prefix", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/prefixes/deleteList")
    async def delete_prefixes(self, prefix: schemas.PrefixBulkDelete):
        results = await self.crud.delete_multi(self.session, prefix.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "prefix", "#ids", prefix.ids)
            return return_info
        return_info = ResponseMsg(data=prefix.ids, locale=self.locale)
        return return_info


@cbv(router)
class VLANGroupCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(VLANGroup)
    locale = Depends(get_locale)

    @router.post("/vlan-groups")
    async def create_vlan_group(self, vlan_group: schemas.VLANGroupCreate) -> BaseResponse[int]:
        local_vlan_group = await self.crud.get_by_field(self.session, "name", vlan_group.name)
        if local_vlan_group:
            return_info = error_404_409(ERR_NUM_409, self.locale, "vlan-group", "name", vlan_group.name)
            return return_info
        new_vlan_group = await self.crud.create(self.session, vlan_group)
        return_info = ResponseMsg(data=new_vlan_group.id)
        return return_info

    @router.get("/vlan-groups/{id}")
    async def get_vlan_group(self, id: int) -> BaseResponse[schemas.VLANGroup]:
        local_vlan_group: VLANGroup = await self.session.get(VLANGroup, id)
        if not local_vlan_group:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan-group", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_vlan_group, locale=self.locale)
        return return_info

    @router.get("/vlan-groups")
    async def get_vlan_groups(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.VLANGroup]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.post("/vlan-groups/getList")
    async def get_vlan_group_filter(
        self, vlan_group: schemas.VLANGroupQuery
    ) -> BaseListResponse[List[schemas.VLANGroup]]:
        pass

    @router.put("/vlan-groups/{id}")
    async def update_vlan_group(self, id: int, vlan_group: schemas.VLANGroupUpdate) -> BaseResponse[int]:
        local_vlan_group: VLANGroup = await self.session.get(VLANGroup, id)
        if not local_vlan_group:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan-group", "#id", id)
            return return_info
        exist_name = await self.crud.get_by_field(self.session, "name", vlan_group.name)
        if exist_name:
            return_info = error_404_409(ERR_NUM_409, self.locale, "vlan-group", "name", vlan_group.name)
            return return_info
        await self.crud.update(self.session, id, vlan_group)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.delete("/vlan-groups/{id}")
    async def delete_vlan_group(self, id) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan-group", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/vlan-groups/deleteList")
    async def delete_vlan_groups(self, vlan_group: schemas.VLANGroupBulkDelete):
        results = await self.crud.delete_multi(self.session, vlan_group.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan-group", "#ids", vlan_group.ids)
            return return_info
        return_info = ResponseMsg(data=vlan_group.ids, locale=self.locale)
        return return_info


@cbv(router)
class VLANCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(VLAN)

    @router.post("/vlans")
    async def create_vlan(self, vlan: schemas.VLANCreate) -> BaseResponse[int]:
        if vlan.site_id:
            site: Site = await self.session.get(VLAN, vlan.site_id)
            if not site:
                return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
                return return_info
        if vlan.role_id:
            role: IPRole = await self.session.get(VLAN, vlan.role_id)
            if not role:
                return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
                return return_info
        exist_vlan = await self.crud.filter(
            self.session,
            filter={
                "site_id": vlan.site_id,
                "vid": vlan.vid,
            },
        )
        if exist_vlan:
            return_info = error_404_409(ERR_NUM_409, self.locale, "vlan", "vlan id", vlan.vid)
            return return_info
        new_vlan = await self.crud.create(self.session, vlan)
        return_info = ResponseMsg(data=new_vlan.id, locale=self.locale)
        return return_info

    @router.get("/vlans/{id}")
    async def get_vlan(self, id: int) -> BaseResponse[schemas.VLAN]:
        local_vlan: VLAN = await self.session.get(VLAN, id)
        if not local_vlan:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_vlan, locale=self.locale)
        return return_info

    @router.get("/vlans")
    async def get_vlans(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.VLAN]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.post("/vlans/getList")
    async def get_vlans_filter(self, vlan: schemas.VLANQuery) -> BaseListResponse[List[schemas.VLAN]]:
        pass

    @router.put("/vlans/{id}")
    async def update_vlan(self, id: int, vlan: schemas.VLANUpdate) -> BaseResponse[int]:
        if vlan.site_id:
            site: Site = await self.session.get(VLAN, vlan.site_id)
            if not site:
                return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
                return return_info
        if vlan.role_id:
            role: IPRole = await self.session.get(VLAN, vlan.role_id)
            if not role:
                return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
                return return_info
        exist_vlan = await self.crud.filter(
            self.session,
            filter={
                "site_id": vlan.site_id,
                "vid": vlan.vid,
            },
        )
        if exist_vlan:
            return_info = error_404_409(ERR_NUM_409, self.locale, "vlan", "vlan id", vlan.vid)
            return return_info

        await self.crud.update(self.session, id, vlan)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/vlans/updateList")
    async def update_vlans(self, vlan: schemas.VLANBulkUpdate) -> BaseResponse[List[int]]:
        results = await self.crud.get_multi(self.session, vlan.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan", "#ids", vlan.ids)
            return return_info
        if len(results) < set(vlan.ids):
            diff_ids = set(vlan.ids) - set([result.id for result in results])
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan", "#ids", list(diff_ids))
            return return_info
        if vlan.site_id:
            site: Site = await self.session.get(VLAN, vlan.site_id)
            if not site:
                return_info = error_404_409(ERR_NUM_404, self.locale, "site", "#id", id)
                return return_info
        if vlan.role_id:
            role: IPRole = await self.session.get(VLAN, vlan.role_id)
            if not role:
                return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
                return return_info
        await self.crud.update_multi(self.session, vlan.ids, vlan, excludes={"ids"})
        return_info = ResponseMsg(data=vlan.ids, locale=self.locale)
        return return_info

    @router.delete("/vlans/{id}")
    async def delete_vlan(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan", "#id", id)
            return return_info
        result_info = ResponseMsg(data=id, locale=self.locale)
        return result_info

    @router.post("/vlans/deleteList")
    async def delete_vlans(self, vlan: schemas.VLANBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, vlan.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "vlan", "#ids", vlan.ids)
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results], locale=self.locale)
        return return_info


@cbv(router)
class IPRangeCVB:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(IPRange)
    locale = Depends(get_locale)

    @router.post("/ip-ranges")
    async def create_ip_range(self, ip_range: schemas.IPRangeCreate) -> BaseResponse[int]:
        if ip_range.vrf_id:
            vrf: VRF = await self.session.get(VRF, id)
            if not vrf:
                return_info = error_404_409(ERR_NUM_404, self.locale, "vrf", "#id", id)
                return return_info
        if ip_range.role_id:
            role: IPRole = await self.session.get(IPRole, id)
            if not role:
                return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
                return return_info
        new_ip_range = await self.crud.create(self.session, ip_range)
        return_info = ResponseMsg(data=new_ip_range.id, locale=self.locale)
        return return_info

    @router.get("/ip-ranges/{id}")
    async def get_ip_range(self, id: int) -> BaseResponse[schemas.IPRange]:
        result: IPRange = await self.session.get(IPRange, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-range", "#id", id)
            return return_info
        return_info = ResponseMsg(data=result, locale=self.locale)
        return return_info

    @router.get("/ip-ranges")
    async def get_ip_ranges(self, q: QueryParams = Depends(QueryParams)) -> BaseListResponse[List[schemas.IPRange]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(data={"count": count, "results": results}, locale=self.locale)
        return return_info

    @router.post("/ip-ranges/getList")
    async def get_ip_ranges_filter(self, ip_range: schemas.IPRangeQuery) -> BaseListResponse[List[BaseResponse]]:
        pass

    @router.put("/ip-ranges/{id}")
    async def update_ip_range(self, ip_range: schemas.IPRangeUpdate) -> BaseResponse[int]:
        local_ip_range: IPRange = await self.session.get(IPRange, id)
        if not local_ip_range:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-range", "#id", id)
            return return_info
        if ip_range.role_id:
            ip_role: IPRole = await self.session.get(IPRole, id)
            if not ip_role:
                return_info = error_404_409(ERR_NUM_404, self.locale, "ip-role", "#id", id)
                return return_info
        if ip_range.vrf_id:
            vrf: VRF = await self.session.get(VRF, id)
            if not vrf:
                return_info = error_404_409(ERR_NUM_404, self.locale, "vrf", "#id", id)
                return return_info
        await self.crud.update(self.session, id, ip_range)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/ip-ranges/updateList")
    async def update_ip_ranges(self):
        pass

    @router.delete("/ip-ranges/{id}")
    async def delete_ip_range(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-range", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/ip-ranges/deleteList")
    async def delete_ip_ranges(self, ip_range: schemas.IPRangeBulkDelete) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, ip_range.ids)
        if not results:
            return_info = error_404_409(ERR_NUM_404, self.locale, "ip-range", "#ids", ip_range.ids)
            return return_info
        return_info = ResponseMsg([result.id for result in results], locale=self.locale)
        return return_info


@cbv(router)
class IPAddressCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(IPRange)

    @router.post("/ip-addresses")
    async def create_ip_address(self, ip_address: schemas.IPAddressCreate) -> BaseResponse[int]:
        pass

    @router.get("ip-addresses/{id}")
    async def get_ip_address(self, id: int) -> BaseResponse[schemas.IPAddress]:
        pass

    @router.get("/ip-addresses")
    async def get_ip_addresses(self, q: schemas.IPAddress):
        pass
