from fastapi import Query
from pydantic import AnyHttpUrl, Field

from src.features import schemas
from src.features._types import AuditTime, BaseModel, I18nField, NameStr, QueryParams


class CircuitTypeCreate(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None


class CircuitTypeUpdate(CircuitTypeCreate):
    name: I18nField | None = None
    slug: str | None


class CircuitTypeQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class CircuitType(CircuitTypeCreate, AuditTime):
    id: int
    circuit_count: int


class DeviceRoleCreate(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None
    priority: int


class DeviceRoleUpdate(BaseModel):
    name: I18nField | None = None
    slug: str | None = None
    priority: int | None = None


class DeviceRoleQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class DeviceRole(DeviceRoleCreate, AuditTime):
    id: int
    device_count: int


class IPRoleCreate(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None


class IPRoleUpdate(BaseModel):
    name: I18nField | None = None
    slug: str | None = None


class IPRoleQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class IPRole(IPRoleCreate, AuditTime):
    id: int
    prefix_count: int
    vlan_count: int


class PlatformBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    netmiko_driver: str | None = None


class PlatformCreate(PlatformBase):
    name: NameStr
    slug: NameStr


class PlatformUpdate(PlatformCreate):
    name: NameStr | None = None
    slug: NameStr | None = None


class PlatformQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class Platform(PlatformBase, AuditTime):
    id: int
    device_type_count: int
    device_count: int
    textfsm_template_count: int


class ManufacturerCreate(BaseModel):
    name: I18nField
    slug: NameStr
    description: str | None = None


class ManufacturerUpdate(ManufacturerCreate):
    name: I18nField | None = None
    slug: NameStr | None = None


class ManufacturerQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[NameStr] | None = Field(Query(default=[]))


class Manufacturer(ManufacturerCreate, AuditTime):
    id: int
    device_type_count: int
    device_count: int


class DeviceTypeBase(BaseModel):
    name: str
    snmp_sysobjectid: str
    u_height: float
    front_image: AnyHttpUrl | None = None
    rear_image: AnyHttpUrl | None = None


class DeviceTypeCreate(DeviceTypeBase):
    name: NameStr
    manufacturer_id: int
    platform_id: int


class DeviceTypeUpdate(DeviceTypeCreate):
    name: NameStr | None = None
    snmp_sysobjectid: str | None = None
    u_height: float | None = None
    manufacturer_id: int | None = None
    platform_id: int | None = None


class DeviceTypeQuery(QueryParams):
    name: list[NameStr] | None = Field(Query(default=[]))
    manufacturer_id: list[int] | None = Field(Query(default=[]))
    platform_id: list[int] | None = Field(Query(default=[]))


class DeviceTypeInfo(DeviceTypeBase):
    id: int
    manufacturer: schemas.ManufacturerBrief
    platform: schemas.PlatformBrief


class DeviceType(DeviceTypeBase, AuditTime):
    id: int
    device_count: int
    manufacturer: schemas.ManufacturerBrief
    platform: schemas.PlatformBrief
