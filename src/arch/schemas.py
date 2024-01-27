from fastapi import Query
from pydantic import Field

from src._types import AuditTime, AuditUser, BaseModel, I18nField, QueryParams
from src.internal import schemas


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


class CircuitType(CircuitTypeCreate, AuditTime, AuditUser):
    id: int
    circuit: list[schemas.CircuitBrief]


class CircuitTypeList(CircuitTypeCreate, AuditTime):
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


class RackRole(RackRoleCreate, AuditTime, AuditUser):
    id: int
    rack_count: int


class RackRoleList(RackRoleCreate, AuditTime):
    id: int
    rack_count: int


class DeviceRoleCreate(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None


class DeviceRoleUpdate(BaseModel):
    name: I18nField | None = None
    slug: str | None = None


class DeviceRoleQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class DeviceRole(DeviceRoleCreate, AuditTime, AuditUser):
    id: int
    device_count: int


class DeviceRoleList(RackRoleCreate, AuditTime):
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


class IPRole(IPRoleCreate, AuditTime, AuditUser):
    id: int


class IPRoleList(RackRoleCreate, AuditTime):
    id: int
