from ipaddress import IPv4Address, IPv6Address

from fastapi import Query
from pydantic import AnyHttpUrl, Field, IPvAnyAddress, model_validator

from src._types import (
    AuditTime,
    AuditTimeQuery,
    BaseModel,
    I18nField,
    IdCreate,
    NameChineseStr,
    NameStr,
    QueryParams,
)
from src.consts import DeviceStatus, EntityPhysicalClass, RackStatus
from src.internal import schemas


class RackBase(BaseModel):
    name: str
    status: RackStatus
    serial_num: str | None = None
    asset_tag: str | None = None
    u_width: float | None = None
    u_height: float | None = None


class RackCreate(RackBase):
    name: NameChineseStr
    site_id: int | None = None
    location_id: int | None = None
    rack_role_id: int


class RackUpdate(RackCreate):
    name: NameChineseStr | None = None
    status: RackStatus | None = Field(
        default=None, description="When rack status is offline, all devices associated will be offlined"
    )
    site_id: int | None = None
    location_id: int | None = None
    rack_role_id: int | None = None


class RackQuery(QueryParams, AuditTimeQuery):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
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
    slug: NameStr
    description: str | None = None


class VendorUpdate(VendorCreate):
    name: I18nField | None = None
    slug: NameStr | None = None


class VendorQuery(QueryParams):
    name: list[str] | None = Field(Query(default=[]))
    slug: list[NameStr] | None = Field(Query(default=[]))


class Vendor(VendorCreate, AuditTime):
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
    vendor_id: int
    platform_id: int


class DeviceTypeUpdate(DeviceTypeCreate):
    name: NameStr | None = None
    snmp_sysobjectid: str | None = None
    u_height: float | None = None
    vendor_id: int | None = None
    platform_id: int | None = None


class DeviceTypeQuery(QueryParams):
    name: list[NameStr] | None = Field(Query(default=[]))
    vendor_id: list[int] | None = Field(Query(default=[]))
    platform_id: list[int] | None = Field(Query(default=[]))


class DeviceTypeInfo(DeviceTypeBase):
    id: int
    vendor: schemas.VendorBrief
    platform: schemas.PlatformBrief


class DeviceType(DeviceTypeBase, AuditTime):
    id: int
    device_count: int
    vendor: schemas.VendorBrief
    platform: schemas.PlatformBrief


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


class DeviceBase(BaseModel):
    name: str
    management_ipv4: IPv4Address | None = None
    management_ipv6: IPv6Address | None = None
    oob_ip: IPvAnyAddress | None = None
    status: DeviceStatus
    version: str | None = None
    serial_num: str | None = None
    asset_tag: str | None = None
    comments: str | None = None


class DeviceCreate(DeviceBase):
    name: NameStr
    device_type_id: int
    device_role_id: int
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
    site_id: int | None = None
    location_id: int | None = None
    rack_id: int | None = None
    device_group_id: int | None = None
    name: NameStr | None = None
    status: DeviceStatus | None = None


class DeviceQuery(QueryParams):
    name: list[NameStr] | None = Field(Query(default=[]))
    status: list[DeviceStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    location_id: list[int] | None = Field(Query(default=[]))
    rack_id: list[int] | None = Field(Query(default=[]))
    device_role_id: list[int] | None = Field(Query(default=[]))
    platform_id: list[int] | None = Field(Query(default=[]))
    vendor_id: list[int] | None = Field(Query(default=[]))
    device_type_id: list[int] | None = Field(Query(default=[]))
    management_ipv4: list[IPv4Address] | None = Field(Query(default=[]))
    management_ipv6: list[IPv6Address] | None = Field(Query(default=[]))


class Device(DeviceBase, AuditTime):
    id: int
    device_type: DeviceTypeInfo
    device_role: schemas.DeviceRoleBrief
    site: schemas.SiteBrief
    location: schemas.LocationBrief
    rack: schemas.RackRoleBrief
    device_group: schemas.DeviceGroupBrief
    interface_count: int
    device_entity_count: int


class DeviceEntityBase(BaseModel):
    index: str
    entity_class: EntityPhysicalClass
    hardware_version: str | None = None
    software_version: str | None = None
    serial_num: str | None = None
    model_name: str | None = None
    asset_id: str | None = None
    order: int


class DeviceEntityCreate(DeviceEntityBase):
    device_id: int


class DeviceEntityUpdate(DeviceEntityBase):
    index: str | None = None
    entity_class: EntityPhysicalClass | None = None
    order: int | None = None
    device_id: int | None = None


class DeviceEntityQuery(QueryParams):
    device_id: list[int] | None = Field(Query(default=[]))
    serial_num: list[str] | None = Field(Query(default=[]))


class DeviceEntity(DeviceEntityBase, AuditTime):
    id: int
    device: schemas.DeviceBrief


class DeviceGroupBase(BaseModel):
    name: str
    description: str | None = None


class DeviceGroupCreate(DeviceGroupBase):
    name: NameChineseStr
    device: list[IdCreate] | None = None


class DeviceGroupUpdate(DeviceGroupCreate):
    name: NameChineseStr | None = None


class DeviceGroupQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))


class DeviceGroup(DeviceGroupBase, AuditTime):
    id: int
    devices: list[schemas.DeviceBrief]


class DeviceGroupList(DeviceGroupBase, AuditTime):
    id: int
    device_count: int
