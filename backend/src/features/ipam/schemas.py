from fastapi import Query
from pydantic import Field, IPvAnyInterface, IPvAnyNetwork, model_validator

from src.features._types import AuditTime, BaseModel, IdCreate, NameChineseStr, NameStr, QueryParams
from src.features.admin.schemas import UserBrief
from src.features.consts import IPRangeStatus, PrefixStatus, VLANStatus
from src.features.internal import schemas


class BlockBase(BaseModel):
    name: str
    block: IPvAnyNetwork
    is_private: bool
    description: str | None = None


class BlockCreate(BaseModel):
    name: NameChineseStr


class BlockUpdate(BlockCreate):
    name: NameChineseStr | None = None
    block: IPvAnyNetwork | None = None
    is_private: bool | None = None


class BlockQuery(QueryParams):
    block: list[IPvAnyNetwork] | None = Field(Query(default=[]))
    is_private: bool | None = None


class Block(BlockBase, AuditTime):
    id: int


class PrefixBase(BaseModel):
    prefix: IPvAnyNetwork
    status: PrefixStatus
    is_dhcp_pool: bool = True
    is_full: bool = False


class PrefixCreate(PrefixBase):
    vlan_id: int | None = None
    site_id: int | None = None
    role_id: int | None = None
    vrf_id: int | None = None


class PrefixUpdate(PrefixCreate):
    prefix: IPvAnyNetwork | None = None
    status: PrefixStatus | None = None
    is_dhcp_pool: bool | None = None
    is_full: bool | None = None


class PrefixQuery(QueryParams):
    prefix: list[IPvAnyNetwork] | None = Field(Query(default=[]))
    status: PrefixStatus | None = None
    id_dhcp_pool: bool | None = None
    is_full: bool | None = None
    vlan_id: list[int] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    role_id: list[int] | None = Field(Query(default=[]))
    vrf_id: list[int] | None = Field(Query(default=[]))


class Prefix(PrefixBase, AuditTime):
    id: int
    site: schemas.SiteBrief
    role: schemas.IPRoleBrief
    vrf: schemas.VRFBrief
    vlan: schemas.VLANBrief
    children_count: int


class ASNBase(BaseModel):
    asn: int
    description: str | None = None


class ASNCreate(ASNBase):
    asn: int = Field(ge=1, le=4294967295)
    isp: list[IdCreate] | None = None
    site: list[IdCreate] | None = None


class ASNUpdate(ASNCreate):
    asn: int | None = Field(default=None, ge=1, le=4294967295)


class ASNQuery(QueryParams):
    asn: list[int] | None = Field(Query(default=[]))


class ASN(ASNBase, AuditTime):
    id: int
    site: list[schemas.SiteBrief]
    isp: list[schemas.ISPBrief]


class ASNList(ASNBase, AuditTime):
    id: int
    site_count: int
    isp_count: int


class IPRangeBase(BaseModel):
    start_address: IPvAnyInterface
    end_address: IPvAnyInterface
    status: IPRangeStatus
    description: str | None = None


class IPRangeCreate(IPRangeBase):
    vrf_id: int | None = None


class IPRangeUpdate(IPRangeCreate):
    start_address: IPvAnyInterface | None = None
    end_address: IPvAnyInterface | None = None
    status: IPRangeStatus | None = None


class IPRangeQuery(QueryParams): ...


class IPRange(IPRangeBase, AuditTime):
    id: int
    vrf: schemas.VRFBrief


class IPAddressBase(BaseModel):
    address: IPvAnyInterface
    version: int | None = None
    status: IPRangeStatus
    dns_name: str | None = None
    description: str | None = None


class IPAddressCreate(IPAddressBase):
    vrf_id: int | None = None
    owner: list[IdCreate] | None = None
    interface_id: int | None = None

    @model_validator(mode="after")
    def version_validate(self):
        self.version = self.address.version
        return self


class IPAddressUpdate(IPAddressCreate):
    address: IPvAnyInterface | None = None
    status: IPRangeStatus | None = None


class IPAddressQuery(QueryParams):
    address: list[IPvAnyInterface] | None = Field(Query(default=[]))
    status: list[IPRangeStatus] | None = Field(Query(default=[]))
    vrf_id: list[int] | None = Field(Query(default=[]))
    interface_id: list[int] | None = Field(Query(default=[]))


class IPAddress(IPAddressBase, AuditTime):
    id: int
    vrf: schemas.VRFBrief
    owner: list[UserBrief]
    interface: schemas.InterfaceToDevice


class VLANBase(BaseModel):
    name: str
    vid: int
    description: str | None = None
    status: VLANStatus


class VLANCreate(VLANBase):
    name: NameStr
    vid: int = Field(ge=1, le=4096)
    site_id: int | None = None
    role_id: int | None = None


class VLANUpdate(VLANCreate):
    name: NameStr | None = None
    vid: int | None = Field(default=None, ge=1, le=4096)
    status: VLANStatus | None = None


class VLANQuery(QueryParams):
    name: list[int] | None = Field(Query(default=[]))
    vid: list[int] | None = Field(Query(default=[]))
    status: list[VLANStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    role_id: list[int] | None = Field(Query(default=[]))


class VLAN(VLANBase, AuditTime):
    id: int
    site: schemas.SiteBrief
    role: schemas.IPRoleBrief


class VRFBase(BaseModel):
    name: NameChineseStr
    rd: str
    enforce_unique: bool = True


class VRFCreate(VRFBase):
    route_target: list[IdCreate] | None = None


class VRFUpdate(VRFCreate):
    name: NameChineseStr | None = None
    rd: str | None = None
    enforce_unique: bool | None = None


class VRFQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    rd: list[str] | None = Field(Query(default=[]))


class VRF(VRFBase, AuditTime):
    id: int
    route_target: list[schemas.RouteTargetBrief]


class RouteTargetBase(BaseModel):
    name: str
    description: str | None = None


class RouteTargetCreate(RouteTargetBase):
    vrf: list[IdCreate] | None = None


class RouteTargetUpdate(RouteTargetCreate):
    name: NameChineseStr | None = None


class RouteTargetQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))


class RouteTarget(RouteTargetBase, AuditTime):
    id: int
    vrf: list[schemas.VRFBrief] | None = None
