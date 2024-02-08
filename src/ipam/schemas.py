from fastapi import Query
from pydantic import Field, IPvAnyInterface, IPvAnyNetwork

from src._types import BaseModel, IdCreate, QueryParams
from src.consts import IPRangeStatus, PrefixStatus
from src.internal import schemas


class BlockCreate(BaseModel):
    name: str
    block: IPvAnyNetwork
    is_private: bool
    description: str | None = None


class BlockUpdate(BlockCreate):
    block: IPvAnyNetwork | None = None
    is_private: bool | None = None


class BlockQuery(QueryParams):
    block: list[IPvAnyNetwork] | None = Field(Query(default=[]))
    is_private: bool | None = None


class Block(BlockCreate):
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


class ASNBase(BaseModel):
    asn: int
    description: str | None = None


class ASNCreate(ASNBase):
    isp: list[IdCreate] | None = None
    site: list[IdCreate] | None = None


class ASNUpdate(ASNCreate):
    asn: int | None


class ASNQuery(QueryParams):
    asn: list[int] | None = Field(Query(default=[]))


class ASN(ASNBase):
    id: int
    site: list[schemas.SiteBrief]
    isp: list[schemas.ISPBrief]


class ASNList(ASNBase):
    id: int
    site_count: int
    isp_count: int


class IPRangeBase(BaseModel):
    start_address: IPvAnyInterface
    end_address: IPvAnyInterface
    status: IPRangeStatus
