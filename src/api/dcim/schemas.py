from ipaddress import IPv4Address, IPv6Address
from typing import List

from pydantic import UUID4, Field, validator

from src.api.base import BaseModel, BaseQuery
from src.api.dcim import constraints
from src.utils.validators import items_to_list


class InterfaceCreate(BaseModel):
    name: str
    description: str | None
    if_index: int | None
    speed: int | None
    model: constraints.INTERFACE_MODE = Field(default="access")
    mtu: int | None = Field(default=1500)
    enabled: bool | None = Field(default=True)
    device_id: int
    lag_interface_id: int | None
    parent_interface_id: int | None
    vrf_id: int | None
    vlan_id: int | None


class InterfaceQuery(BaseQuery):
    pass


class InterfaceUpdate(InterfaceCreate):
    name: str | None
    device_id: int | None


class InterfaceBulkUpdate(BaseModel):
    ids: List[int]
    description: str | None
    speed: int | None
    model: constraints.INTERFACE_MODE | None
    mtu: int | None
    enabled: int | None
    lag_interface_id: int | None
    parent_interface_id: int | None
    vrf_id: int | None
    vlan_id: int | None


class InterfaceBase(InterfaceCreate):
    id: int


class Interface(InterfaceBase):
    pass


class DeviceRoleCreate(BaseModel):
    name: str
    description: str | None
    vm_role: bool = False


class DeviceRoleQuery(BaseQuery):
    pass


class DeviceRoleUpdate(DeviceRoleCreate):
    name: str | None


class DeviceRoleBulkDelete(BaseModel):
    ids: list[int]


class DeviceRoleBase(DeviceRoleCreate):
    id: int


class DeviceRole(DeviceRoleBase):
    pass


class PlatformCreate(BaseModel):
    name: str
    description: str | None
    netdev_platform: constraints.NETDEV_PLATFORM | None


class PlatformQuery(BaseQuery):
    pass


class PlatformUpdate(PlatformCreate):
    name: str | None


class PlatformBulkUpdate(BaseModel):
    description: str | None
    netdev_platform: constraints.NETDEV_PLATFORM | None


class PlatformBulkDelete(BaseModel):
    ids: list[int]


class PlatformBase(PlatformCreate):
    id: int


class Platform(PlatformBase):
    pass


class ManufacturerCreate(BaseModel):
    name: str
    description: str | None
    device_type_ids: int | List[int] | None

    @validator("device_type_ids")
    def id_trans(cls, v):
        v = items_to_list(v)
        return v


class ManufacturerQuery(BaseQuery):
    pass


class ManufacturerUpdate(ManufacturerCreate):
    name: str | None


class ManufacturerBulkDelete(BaseModel):
    ids: List[int]


class ManufacturerBase(BaseModel):
    id: int
    name: str
    description: str | None


class Manufacturer(BaseModel):
    pass


class DeviceTypeCreate(BaseModel):
    name: str
    description: str | None
    manufacturer_id: int | None
    u_height: float = Field(default=1.0)
    is_full_depth: bool = True
    front_image: UUID4 | None
    rear_image: UUID4 | None


class DeviceTypeQuery(BaseQuery):
    pass


class DeviceTypeUpdate(DeviceRoleCreate):
    name: str | None
    u_height: float | None
    is_full_depth: bool | None


class DeviceTypeBulkDelete(BaseModel):
    ids: List[int]


class DeviceTypeBase(DeviceTypeCreate):
    int


class DeviceType(BaseModel):
    pass


class DeviceCreate(BaseModel):
    name: str
    primary_ipv4: IPv4Address | None
    primary_ipv6: IPv6Address | None
    description: str | None
    device_type_id: int
    device_role_id: int
    platform_id: int
    site_id: int
    location_id: int | None
    rack_id: int | None
    manufacturer_id: int
    position: float | None
    serial_num: str | None
    asset_tag: str | None
    status: constraints.DEVICE_STATUS
    cluster_id: int | None
    comments: str | None
    department_id: int | None


class DeviceQuery(BaseQuery):
    pass


class DeviceUpdate(DeviceCreate):
    name: str | None
    device_type_id: int | None
    device_role_id: int | None
    platform_id: int | None
    site_id: int | None
    manufacturer_id: int | None
    status: constraints.DEVICE_STATUS | None


class DeviceBulkUpdate(BaseModel):
    description: str | None
    device_type_id: int | None
    device_role_id: int | None
    platform_id: int | None
    site_id: int | None
    location_id: int | None
    rack_id: int | None
    manufacturer_id: int | None
    status: constraints.DEVICE_STATUS | None
    cluster_id: int | None
    comments: str | None
    department_id: int | None


class DeviceBulkDelete(BaseModel):
    ids: List[int]


class DeviceBase(DeviceCreate):
    id: int


class Device(BaseModel):
    pass


class RackRoleCreate(BaseModel):
    name: str
    description: str | None


class RackRoleQuery(BaseQuery):
    pass


class RackRoleUpdate(RackRoleCreate):
    name: str | None


class RackRoleBulkDelete(BaseModel):
    ids: List[int]


class RackRoleBase(RackRoleCreate):
    id: int


class RackRole(BaseModel):
    pass


class RackCreate(BaseModel):
    name: str
    description: str | None
    facility_id: str | None
    site_id: int
    location_id: int | None
    status: constraints.RACK_STATUS
    serial_num: List[str] | None
    asset_tag: str | None
    width: int | None
    u_height: int | None
    rack_role_id: int
    desc_units: bool = False
    outer_width: int | None
    outer_depth: int | None
    outer_unit: str | None
    comments: str | None


class RackQuery(BaseQuery):
    pass


class RackUpdate(RackCreate):
    name: str | None
    site_id: int | None
    device_ids: List[int] | None
    status: constraints.RACK_STATUS | None
    rack_role_id: int | None
    desc_units: bool | None


class RackBulkUpdate(BaseModel):
    description: str | None
    facility_id: str | None
    site_id: int | None
    status: constraints.RACK_STATUS | None
    width: int | None
    u_height: int | None
    rack_role_id: int
    desc_units: bool = False
    outer_width: int | None
    outer_depth: int | None
    outer_unit: str | None
    comments: str | None


class RackBulkDelete(BaseModel):
    ids: List[int]


class RackBase(RackCreate):
    id: int


class Rack(BaseModel):
    pass


class LocationCreate(BaseModel):
    name: str
    description: str | None
    status: constraints.LOCATION_STATUS
    parent_id: int | None
    site_id: int


class LocationQuery(BaseQuery):
    pass


class LocationUpdate(LocationCreate):
    name: str | None
    site_id: int | None
    status: constraints.LOCATION_STATUS | None


class LocationBulkDelete(BaseModel):
    ids: List[int]


class LocationBase(LocationCreate):
    id: int


class Location(BaseModel):
    pass


class SiteCreate(BaseModel):
    name: str = Field(description="Unique name of the site")
    description: str | None
    site_code: str = Field(
        description="Recommended use airport code of the city as prefix and auto-increment number as suffix, e.g. `CNCTU01`, `CNPEK01"
    )
    status: constraints.SITE_STATUS
    region_id: int = Field(
        description="cannot be empty, aims to build standard network"
    )
    facility: str | None
    ipam_asn_ids: List[int] | None
    time_zone: constraints.ALL_TIME_ZONES
    physical_address: str
    shipping_address: str | None
    latitude: float | None
    longitude: float | None
    classification: constraints.SITE_CLASSIFICATIONS
    functions: List[str] | None = Field(
        description="a set of tags to mark the function of the sites, e.g.`RD`, `Sales`, `Mixed`"
    )
    contact_ids: List[int] | None


class SiteQuery(BaseQuery):
    ids: List[int] | None
    name: str | None
    site_code: str | None
    status: constraints.SITE_STATUS | None


class SiteUpdate(SiteCreate):
    name: str | None
    site_code: str | None
    status: constraints.SITE_STATUS | None
    region_id: int | None
    time_zone: constraints.ALL_TIME_ZONES | None
    physical_address: str | None
    classification: constraints.SITE_CLASSIFICATIONS | None


class SiteBulkUpdate(BaseModel):
    ids: List[int]
    status: constraints.SITE_STATUS | None
    region_id: int | None
    time_zone: constraints.ALL_TIME_ZONES | None
    classification: constraints.SITE_CLASSIFICATIONS | None
    functions: List[str] | None
    contact_ids: List[int] | None


class SiteBulkDelete(BaseModel):
    ids: List[int]


class SiteBase(SiteCreate):
    id: int


class Site(BaseModel):
    pass


class RegionCreate(BaseModel):
    name: str
    description: str | None
    parent_id: int | None


class RegionQuery(BaseQuery):
    pass


class RegionUpdate(RegionCreate):
    name: str | None


class RegionBulkUpdate(BaseModel):
    description: str | None
    parent_id: int | None


class RegionBulkDelete(BaseModel):
    ids: List[int]


class RegionBase(RegionCreate):
    id: int


class Region(BaseModel):
    pass
