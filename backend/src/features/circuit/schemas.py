from datetime import date

from fastapi import Query
from pydantic import AnyHttpUrl, EmailStr, Field, IPvAnyAddress, IPvAnyNetwork

from src.features import schemas
from src.features._types import (
    AuditTime,
    AuditTimeQuery,
    AuditUser,
    BaseModel,
    BatchUpdate,
    I18nField,
    NameChineseStr,
    NameStr,
    QueryParams,
)
from src.features.consts import CircuitStatus


class ISPBase(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None
    account: str | None = None
    portal: AnyHttpUrl | None = None
    noc_contact: list[EmailStr] | None = None
    admin_contact: list[EmailStr] | None = None
    comments: str | None = None


class ISPCreate(ISPBase):
    slug: NameStr
    asn: list[int] | None = Field(default=None, description="List of asn id belong to current isp.")


class ISPUpdate(ISPCreate):
    name: I18nField | None = None
    slug: NameStr | None = None


class ISP(ISPBase, AuditTime):
    id: int
    asn: list[schemas.ASNBrief]


class ISPList(ISPBase, AuditTime):
    id: int
    asn_count: int = Field(description="Number of as number belongs to current isp.")


class ISPQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[NameStr] | None = Field(Query(default=[]))


class CircuitBase(BaseModel):
    name: str
    slug: str
    cid: str
    status: CircuitStatus
    install_date: date | None = None
    purchase_term: str | None = None
    bandwidth: int
    comments: str | None = None
    vender_available_ip: list[IPvAnyNetwork] | None = None
    vender_available_gateway: list[IPvAnyAddress] | None = None


class CircuitCreate(CircuitBase):
    name: NameChineseStr
    slug: NameStr
    isp_id: int
    circuit_type_id: int
    bandwidth: int = Field(gt=0, description="Mbps")
    interface_a_id: int
    interface_z_id: int | None = None


class CircuitUpdate(CircuitCreate):
    name: NameChineseStr | None = None
    slug: NameStr | None = None
    cid: str | None = None
    status: CircuitStatus | None = None
    bandwidth: int | None = Field(default=None, gt=0, description="Mbps")
    isp_id: int | None = None
    circuit_type_id: int | None = None
    interface_a_id: int | None = None


class CircuitBatchUpdate(BatchUpdate):
    status: CircuitStatus | None = None
    isp_id: int | None = None
    circuit_type_id: int | None = None


class CircuitQuery(QueryParams, AuditTimeQuery):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
    slug: list[NameStr] | None = Field(Query(default=[]))
    cid: list[str] | None = Field(Query(default=[]))
    status: CircuitStatus | None = Field(Query(default=[]))
    install_date__lte: date | None = None
    install_date__gte: date | None = None
    bandwidth__lte: int | None = None
    bandwidth__gte: int | None = None
    isp_id: list[int] | None = Field(Query(default=[]))
    circuit_type_id: list[int] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    device_id: list[int] | None = Field(Query(default=[]))


class Circuit(CircuitBase, AuditUser):
    id: int
    isp: schemas.ISPBrief
    circuit_type: schemas.CircuitTypeBrief
    site_a: schemas.SiteBrief
    devie_a: schemas.DeviceBrief
    interface_a: schemas.InterfaceBrief
    site_z: schemas.SiteBrief | None = None
    devie_z: schemas.DeviceBrief | None = None
    interface_z: schemas.InterfaceBrief | None = None


class CirctuiList(CircuitBase, AuditTime):
    id: int
    isp: schemas.ISPBrief
    circuit_type: schemas.CircuitTypeBrief
    site_a: schemas.SiteBrief
    devie_a: schemas.DeviceBrief
    interface_a: schemas.InterfaceBrief
    site_z: schemas.SiteBrief | None = None
    devie_z: schemas.DeviceBrief | None = None
    interface_z: schemas.InterfaceBrief | None = None
