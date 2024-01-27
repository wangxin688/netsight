from ipaddress import IPv4Address, IPv6Address

from fastapi import Query
from pydantic import AnyHttpUrl, Field, model_validator

from src._types import (
    AuditTime,
    AuditTimeQuery,
    AuditUser,
    BaseModel,
    I18nField,
    NameStr,
    QueryParams,
)
from src.consts import DeviceStatus, RackStatus
from src.internal import schemas


class RackBase(BaseModel):
    name: str
    status: RackStatus
    serial_num: str | None = None
    asset_tag: str | None = None
    u_width: float | None = None
    u_height: float | None = None


class RackCreate(RackBase):
    site_id: int | None = None
    location_id: int | None = None
    rack_role_id: int


class RackUpdate(RackCreate):
    name: str | None = None
    status: RackStatus | None = None
    rack_role_id: int | None = None


class RackQuery(QueryParams, AuditTimeQuery):
    name: list[str] | None = Field(Query(default=[]))
    status: list[RackStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    location_id: list[int] | None = Field(Query(default=[]))
    rack_role_id: list[int] | None = Field(Query(default=[]))


class Rack(RackBase, AuditTime):
    site: schemas.SiteBrief
    location: schemas.LocationBrief
    rack_role: schemas.RackRoleBrief
    device_count: int


class VendorCreate(BaseModel):
    name: I18nField
    slug: str
    description: str | None = None


class VendorUpdate(VendorCreate):
    name: I18nField | None = None
    slug: str | None = None


class VendorQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))


class Vendor(VendorCreate, AuditTime, AuditUser):
    id: int
    device_type_count: int
    platform_count: int


class VendorList(VendorCreate, AuditTime):
    id: int
    device_type_count: int
    platform_count: int


class DeviceTypeBase(BaseModel):
    name: str
    snmp_sysobjectid: str
    u_height: float
    front_image: AnyHttpUrl | None = None
    rear_image: AnyHttpUrl | None = None


class DeviceTypeCreate(DeviceTypeBase):
    vendor_id: int


class DeviceTypeUpdate(DeviceTypeCreate):
    name: str | None = None
    snmp_sysobjectid: str | None = None
    u_height: float | None = None
    vendor_id: int | None = None


class DeviceTypeQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    vendor_id: list[int] | None = Field(Query(default=[]))


class DeviceTypeList(DeviceTypeBase, AuditTime):
    id: int
    device_count: int
    vendor: schemas.VendorBrief


class DeviceType(DeviceTypeBase, AuditTime, AuditUser):
    id: int
    device_count: int
    vendor: schemas.VendorBrief


class PlatformBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    netmiko_driver: str | None = None


class PlatformCreate(PlatformBase):
    vendor_id: int


class PlatformUpdate(PlatformCreate):
    name: str | None = None
    slug: str | None = None
    vendor_id: int | None = None


class PlatformQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[str] | None = Field(Query(default=[]))
    vendor_id: list[int] | None = Field(Query(default=[]))


class Platform(PlatformBase, AuditTime, AuditUser):
    id: int
    device_count: int
    vendor: schemas.VendorBrief


class DeviceBase(BaseModel):
    name: NameStr
    management_ipv4: IPv4Address | None = None
    management_ipv6: IPv6Address | None = None
    status: DeviceStatus
    version: str | None = None
    serial_num: str | None = None
    asset_tag: str | None = None
    comments: str | None = None


class DeviceCreate(DeviceBase):
    device_type_id: int
    device_role_id: int
    platform_id: int
    site_id: int | None = None
    location_id: int | None = None
    rack_id: int | None = None
    device_group_id: int | None = None

    @model_validator(mode="after")
    def validate_device_create(self) -> "DeviceCreate":
        if not self.management_ipv4 and not self.management_ipv6:
            raise ValueError("Management IPv4 or IPv6 address must be specified any one of them")
        if not self.site_id and not self.location_id:
            raise ValueError("Site or Location must be specified any one of them")
        return self


class DeviceUpdate(DeviceBase):
    device_type_id: int | None = None
    device_role_id: int | None = None
    platform_id: int | None = None
    site_id: int | None = None
    location_id: int | None = None
    rack_id: int | None = None
    device_group_id: int | None = None
    name: NameStr | None = None
    status: DeviceStatus | None = None


class DeviceQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    status: list[DeviceStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    location_id: list[int] | None = Field(Query(default=[]))
    rack_id: list[int] | None = Field(Query(default=[]))
    device_role_id: list[int] | None = Field(Query(default=[]))
    platform_id: list[int] | None = Field(Query(default=[]))
    device_type_id: list[int] | None = Field(Query(default=[]))
    management_ipv4: list[IPv4Address] | None = Field(Query(default=[]))
    management_ipv6: list[IPv6Address] | None = Field(Query(default=[]))


class Device(DeviceBase, AuditTime):
    id: int
    device_type: schemas.DeviceTypeBrief
    device_role: schemas.DeviceRoleBrief
    platform: schemas.PlatformBrief
    site: schemas.SiteBrief
    location: schemas.LocationBrief
    rack: schemas.RackRoleBrief
    device_group: schemas.DeviceGroupBrief
