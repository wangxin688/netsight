from datetime import datetime
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import List, Optional

from pydantic import Field, root_validator

from src.api.base import BaseModel, BaseQuery
from src.api.dcim.schemas import InterfaceBase, SiteBase
from src.api.ipam.constraints import (
    IP_STATUS,
    IP_VERSION,
    IPADDRESS_STATUS,
    VLAN_STATUS,
)


class VRFBase(BaseModel):
    id: int
    name: str
    description: str | None
    rd: str
    enforce_unique: bool

    class Config:
        orm_mode = True


class RouteTargetBase(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


class ASNBase(BaseModel):
    id: int
    asn: int
    description: str | None

    class Config:
        orm_mode = True


class VLANBase(BaseModel):
    id: int
    name: str
    description: str
    status: VLAN_STATUS
    vid: int

    class Config:
        orm_mode = True


class IPRangeBase(BaseModel):
    id: int
    start_address: IPv4Address | IPv6Address
    end_address: IPv4Address | IPv6Address
    status: VLAN_STATUS
    description: str | None


class VLANGroupBase(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


class IPRoleBase(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


class IPRole(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


class RIRBase(BaseModel):
    id: int
    name: str
    description: str | None
    is_private: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class BlockBase(BaseModel):
    id: int
    block: IPv4Network | IPv6Network
    description: str | None


class PrefixBase(BaseModel):
    id: int
    prefix: IPv4Network | IPv6Network
    status: IPADDRESS_STATUS
    is_pool: bool
    is_full: bool


class VLAN(BaseModel):
    id: int
    name: str
    description: str
    status: VLAN_STATUS
    dcim_site: SiteBase
    ipam_vlan_group: Optional[VLANGroupBase]
    vid: int
    ipam_role: IPRoleBase
    dcim_interface: List[InterfaceBase]

    class Config:
        orm_mode = True


class RIR(BaseModel):
    id: int
    name: str
    description: str | None
    is_private: bool
    created_at: datetime
    updated_at: datetime | None
    # ipam_block: List[Block] | None

    class Config:
        orm_mode = True


class VLANGroup(BaseModel):
    id: int
    name: str
    description: str | None
    ipam_vlan: List[VLANBase]

    class Config:
        orm_mode = True


class Block(BaseModel):
    id: int
    block: IPv4Network | IPv6Network
    description: str | None
    ipam_rir: RIRBase

    class Config:
        orm_mode = True


class Prefix(BaseModel):
    id: int
    prefix: IPv4Network | IPv6Network
    status: IPADDRESS_STATUS
    dcim_site: SiteBase
    ipam_role: IPRoleBase
    is_pool: bool
    is_full: bool


class ASN(BaseModel):
    id: int
    asn: int
    description: str | None
    dcim_site: List[SiteBase]


class IPRange(BaseModel):
    id: int
    start_address: IPv4Address | IPv6Address
    end_address: IPv4Address | IPv6Address
    status: VLAN_STATUS
    ipam_vrf: VRFBase | None
    ipam_role: IPRoleBase | None
    description: str | None


class IPAddress(BaseModel):
    id: int
    address: IPv4Address | IPv6Address
    ipam_vrf: VRFBase | None
    version: IP_VERSION
    status: IP_STATUS
    dns_name: str | None
    description: str | None
    owners: str
    dcim_interface: InterfaceBase


class IPAddressBase(BaseModel):
    id: int
    address: IPv4Address | IPv6Address
    version: IP_VERSION
    status: IP_STATUS
    dns_name: str | None
    description: str | None
    owners: str | None


class RIRCreate(BaseModel):
    name: IPv4Network | IPv6Network
    description: str | None
    is_private: bool


class RIRUpdate(BaseModel):
    name: IPv4Network | IPv6Network | None
    description: str | None
    is_private: bool | None


class RIRQuery(BaseQuery):
    pass


class RIRBulkDelete(BaseModel):
    ids: List[int]


class BlockCreate(BaseModel):
    block: IPv4Network | IPv6Network
    rir_id: int
    description: str | None


class BlockUpdate(BaseModel):
    Block: IPv4Network | IPv6Network | None
    rir_id: int | None
    description: str | None


class BlockQuery(BaseQuery):
    pass


class BlockBulkDelete(BaseModel):
    ids: List[int]


class IPRoleCreate(BaseModel):
    name: str
    description: str | None


class IPRoleUpdate(BaseModel):
    name: str | None
    description: str | None


class IPRoleQuery(BaseQuery):
    pass


class IPRoleBulkDelete(BaseModel):
    ids: List[int]


class PrefixCreate(BaseModel):
    prefix: IPv4Network | IPv6Network
    status: IPADDRESS_STATUS
    site_id: int
    role_id: int
    is_pool: bool = False
    is_full: bool = False


class PrefixUpdate(BaseModel):
    prefix: IPv4Network | IPv6Network | None
    status: IPADDRESS_STATUS | None
    site_id: int | None
    role_id: int | None
    is_pool: bool | None
    is_full: bool | None


class PrefixBulkUpdate(BaseModel):
    status: IPADDRESS_STATUS | None
    site_id: int | None
    role_id: int | None
    is_pool: bool | None
    is_full: bool | None


class PrefixQuery(BaseQuery):
    pass


class PrefixBulkDelete(BaseModel):
    ids: List[int]


class ASNCreate(BaseModel):
    asn: int = Field(
        gte=0, description="AS number, 64512~65534 as private, RFC4893, RFC1771"
    )
    description: str | None
    site_id: List[int] | None


class ASNUpdate(BaseModel):
    ans: int | None = Field(
        gte=0, description="AS number, 64512~65534 as private, RFC4893, RFC1771"
    )
    description: str | None
    site_id: List[int] | None


class ASNBulkUpdate(BaseModel):
    description: str | None
    site_id: List[int] | None


class ASNQuery(BaseQuery):
    pass


class ASNBulkDelete(BaseModel):
    ids: List[int]


class IPAddressCreate(BaseModel):
    address: IPv4Address | IPv6Address
    version: IP_VERSION
    status: IP_STATUS
    dns_name: str | None
    description: str | None
    owners: str | None
    interface_id: int | None
    vrf_id: int | None

    @root_validator(pre=False)
    def ip_validate(cls, values):
        values["version"] = values["address"].version
        return values


class IPAddressBulkCreate(BaseModel):
    address: List[IPv4Address] | List[IPv6Address]
    version: IP_VERSION
    status: IP_STATUS
    dns_name: str | None
    description: str | None
    owners: str | None
    interface_id: int | None
    vrf_id: int | None

    @root_validator(pre=False)
    def ip_validate(cls, values):
        values["version"] = values["address"].version
        return values


class IPAddressUpdate(BaseModel):
    address: IPv4Address | IPv6Address | None
    version: IP_VERSION | None
    status: IP_STATUS | None
    dns_name: str | None
    description: str | None
    owners: str | None
    interface_id: int | None
    vrf_id: int | None

    @root_validator(pre=False)
    def ip_validate(cls, values):
        if values["address"]:
            values["version"] = values["address"].version
            return values
        return values


class IPAddressBulkUpdate(BaseModel):
    ids: List[int]
    status: IP_STATUS | None
    dns_name: str | None
    description: str | None
    owners: str | None
    interface_id: int | None
    vrf_id: int | None


class IPAddressBulkDelete(BaseModel):
    ids: List[int]
