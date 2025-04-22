from datetime import datetime

from fastapi import Query
from pydantic import Field, IPvAnyAddress, model_validator

from netsight.features import schemas
from netsight.features._types import (
    AuditTime,
    AuditUser,
    BaseModel,
    NameStr,
    QueryParams,
)
from netsight.features.consts import APMode, DeviceEquipmentType, DeviceStatus, InterfaceAdminStatus


class DeviceBase(BaseModel):
    name: str
    management_ip: IPvAnyAddress
    oob_ip: IPvAnyAddress | None = None
    status: DeviceStatus
    software_version: str | None = None
    software_patch: str | None = None
    serial_num: str | None = None
    asset_tag: str | None = None
    comments: str | None = None
    associated_wac_ip: IPvAnyAddress | None = None
    ap_group: str | None = None
    ap_mode: APMode | None = None


class DeviceCreate(DeviceBase):
    name: NameStr
    device_type_id: int
    device_role_id: int = Field(description="when device role is not AP, AP related fields will be ignored")
    site_id: int = Field(default=None)
    location_id: int | None = Field(
        default=None,
        description="if location_id and site_id both set, location_id will be used as higher priority incase of conflict",
    )


class DeviceUpdate(DeviceBase):
    management_ip: IPvAnyAddress | None = None
    device_type_id: int | None = None
    device_role_id: int | None = Field(
        default=None, description="when device role is not AP, AP related fields will be ignored"
    )
    site_id: int | None = Field(
        default=None,
        description="if location_id and site_id both set, location_id will be used as higher priority incase of conflict",
    )
    location_id: int | None = Field(
        default=None,
        description="if location_id and site_id both set, location_id will be used as higher priority incase of conflict. if location_id changed, device's site_id will follow the new location's site_id",
    )
    name: NameStr | None = None
    status: DeviceStatus | None = None

    @model_validator(mode="after")
    def valiate_input(self):
        if self.location_id and self.site_id:
            self.site_id = None
        return self


class DeviceQuery(QueryParams):
    name: list[NameStr] | None = Field(Query(default=[]))
    status: list[DeviceStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    location_id: list[int] | None = Field(Query(default=[]))
    device_role_id: list[int] | None = Field(Query(default=[]))
    platform_id: list[int] | None = Field(Query(default=[]))
    manufacturer_id: list[int] | None = Field(Query(default=[]))
    device_type_id: list[int] | None = Field(Query(default=[]))
    management_ip: list[IPvAnyAddress] | None = Field(Query(default=[]))
    associated_wac_ip: list[IPvAnyAddress] | None = Field(Query(default=[]))
    ap_group: list[str] | None = Field(Query(default=[]))
    ap_mode: APMode | None = Field(Query(default=None))


class Device(DeviceBase, AuditUser):
    id: int
    device_type: schemas.DeviceTypeBrief
    device_role: schemas.DeviceRoleBrief
    platform: schemas.PlatformBrief
    manufacturer: schemas.ManufacturerBrief
    site: schemas.SiteBrief
    location: schemas.LocationBrief | None = None


class DeviceList(DeviceBase, AuditTime):
    id: int
    device_type: schemas.DeviceTypeBrief
    device_role: schemas.DeviceRoleBrief
    platform: schemas.PlatformBrief
    manufacturer: schemas.ManufacturerBrief
    site: schemas.SiteBrief
    location: schemas.LocationBrief | None = None


class DeviceModule(AuditTime):
    id: int
    name: str
    description: str | None = None
    serial_number: str | None = None
    part_number: str | None = None
    hardware_version: str | None = None
    physical_index: int | None = None
    replaceable: bool | None = None


class DeviceStack(AuditTime):
    id: int
    role: str
    mac_address: str
    priority: int | None = None
    device_type: str


class DeviceEquipment(AuditTime):
    id: int
    name: str
    eq_type: DeviceEquipmentType
    description: str | None = None
    device_type: str
    serial_number: str | None = None


class Configuration(BaseModel):
    id: int
    configuration: str
    total_lines: int
    lines_added: int
    lines_deleted: int
    lines_updated: int
    md5_checksum: str | None
    created_by: str
    created_at: datetime
    change_event: dict | None


class Interface(AuditTime):
    id: int
    name: str
    description: str | None = None
    if_index: int | None
    speed: int | None
    mode: str
    interface_type: str | None
    mtu: int | None
    admin_status: InterfaceAdminStatus
    vlan: schemas.VLANBrief | None = None


class Node(BaseModel): ...


class Link(BaseModel): ...


class Topology(BaseModel):
    nodes: list[Node]
    links: list[Link]


class MacAddress(BaseModel): ...


class Route(BaseModel): ...
