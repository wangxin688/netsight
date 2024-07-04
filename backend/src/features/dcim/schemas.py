from ipaddress import IPv4Address, IPv6Address

from fastapi import Query
from pydantic import Field, IPvAnyAddress, model_validator

from src.features._types import (
    AuditTime,
    BaseModel,
    NameStr,
    QueryParams,
)
from src.features.consts import DeviceStatus, EntityPhysicalClass
from src.features.internal import schemas


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

    @model_validator(mode="after")
    def validate_device_create(self):
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
    name: NameStr | None = None
    status: DeviceStatus | None = None


class DeviceQuery(QueryParams):
    name: list[NameStr] | None = Field(Query(default=[]))
    status: list[DeviceStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    location_id: list[int] | None = Field(Query(default=[]))
    device_role_id: list[int] | None = Field(Query(default=[]))
    platform_id: list[int] | None = Field(Query(default=[]))
    manufacturer_id: list[int] | None = Field(Query(default=[]))
    device_type_id: list[int] | None = Field(Query(default=[]))
    management_ipv4: list[IPv4Address] | None = Field(Query(default=[]))
    management_ipv6: list[IPv6Address] | None = Field(Query(default=[]))


class Device(DeviceBase, AuditTime):
    id: int
    device_type: schemas.DeviceTypeBrief
    device_role: schemas.DeviceRoleBrief
    site: schemas.SiteBrief
    location: schemas.LocationBrief | None = None
    interface_count: int
    device_entity_count: int


class DeviceEntityBase(BaseModel):
    index: str
    entity_class: EntityPhysicalClass
    hardware_version: str | None = None
    software_version: str | None = None
    serial_num: str | None = None
    module_name: str | None = None
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


class ConfigSyslogEvent(BaseModel):
    username: str
    config_method: str
    login_ip: IPvAnyAddress
