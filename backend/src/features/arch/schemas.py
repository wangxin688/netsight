from fastapi import Query
from pydantic import Field

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


class RackRoleCreate(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None


class RackRoleUpdate(RackRoleCreate):
    name: I18nField | None = None
    slug: str | None = None


class RackRoleQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class RackRole(RackRoleCreate, AuditTime):
    id: int
    rack_count: int


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
