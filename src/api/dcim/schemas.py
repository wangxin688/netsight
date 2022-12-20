from typing import List

from pydantic import UUID4, Field, validator

from src.api.base import BaseModel, BaseQuery
from src.api.dcim import constraints
from src.utils.validators import items_to_list


class Location(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int
    # dcim_rack: List[Rack] | None
    # dcim_device: List[Device] | None


class LocationBase(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int


class RackRole(BaseModel):
    id: int
    name: str
    description: str | None


class RackRoleBase(BaseModel):
    pass


class Rack(BaseModel):
    pass


class RackBase(BaseModel):
    pass


class Manufacturer(BaseModel):
    pass


class ManufacturerBase(BaseModel):
    pass


class DeviceType(BaseModel):
    pass


class DeviceTypeBase(BaseModel):
    pass


class DeviceRole(BaseModel):
    pass


class DeviceRoleBase(BaseModel):
    pass


class Interface(BaseModel):
    pass


class InterfaceBase(BaseModel):
    pass


class Platform(BaseModel):
    pass


class PlatformBase(BaseModel):
    pass


class RegionBase(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


class Region(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int | None

    class Config:
        orm_mode = True


class SiteBase(BaseModel):
    id: int
    name: str
    site_code: str
    status: str
    classification: str | None

    class Config:
        orm_mode = True


class Site(BaseModel):
    id: int
    name: str
    site_code: str
    status: str
    dcim_region: RegionBase | None
    facility: str | None
    # ipam_asn: List[ASN] | None
    time_zone: str | None
    physical_address: str | None
    shipping_address: str | None
    latitude: float | None
    longitude: float | None
    classification: str | None
    functions: List[str] | None
    # contact: List[Contact] | None
    # dcim_location: List[Location] | None
    # dcim_rack: List[Rack] | None
    # dcim_device: List[Device] | None
    # ipam_prefix: List[Prefix] | None
    # ipam_vlan: List[Vlan] | None
    # circuit_termination: List[CircuitTermination] | None
    # dcim_region: List[RegionBase] | None


class RegionCreate(BaseModel):
    name: str
    description: str | None
    parent_id: int | None


class RegionQuery(BaseQuery):
    ids: List[int] | None
    name: List[str] | None


class RegionUpdate(BaseModel):
    name: str | None
    description: str | None
    parent_id: int | None


class RegionBulkUpdate(BaseModel):
    ids: List[int]
    description: str | None
    parent_id: int | None


class RegionBulkDelete(BaseModel):
    ids: List[int]


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


class SiteUpdate(BaseModel):
    name: str | None = Field(description="Unique name of the site")
    description: str | None
    site_code: str | None = Field(
        description="Recommended use airport code of the city as prefix and auto-increment number as suffix, e.g. `CNCTU01`, `CNPEK01"
    )
    status: constraints.SITE_STATUS | None
    region_id: int | None = Field(
        description="cannot be empty, aims to build standard network"
    )
    facility: str | None
    ipam_asn_ids: List[int] | None
    time_zone: constraints.ALL_TIME_ZONES | None
    physical_address: str | None
    shipping_address: str | None
    latitude: float | None
    longitude: float | None
    classification: constraints.SITE_CLASSIFICATIONS | None
    functions: List[str] | None = Field(
        description="a set of tags to mark the function of the sites, e.g.`RD`, `Sales`, `Mixed`"
    )
    contact_ids: List[int] | None


class SiteBulkUpdate(BaseModel):
    ids: List[int]
    region_id: int | None
    time_zone: constraints.ALL_TIME_ZONES | None
    classification: constraints.SITE_CLASSIFICATIONS | None
    functions: List[str] | None = Field(
        description="a set of tags to mark the function of the sites, e.g.`RD`, `Sales`, `Mixed`"
    )
    contact_ids: List[int] | None


class SiteBulkDelete(BaseModel):
    ids: List[int]


class LocationCreate(BaseModel):
    name: str
    description: str | None
    status: constraints.LOCATION_STATUS
    parent_id: int | None
    site_id: int


class LocationQuery(BaseQuery):
    ids: List[int] | None
    name: str | None
    site_id: int | None


class LocationUpdate(BaseModel):
    name: str | None
    description: str | None
    status: constraints.LOCATION_STATUS | None
    parent_id: int | None
    dcim_site_id: int | None


class LocationBulkUpdate(BaseModel):
    ids: List[int]
    status: constraints.LOCATION_STATUS | None
    parent_id: int | None
    dcim_site_id: int | None


class LocationBulkDelete(BaseModel):
    ids: List[int]


class RackRoleCreate(BaseModel):
    name: str
    description: str | None


class RackRoleQuery(BaseQuery):
    id: List[int] | None
    name: str | None


class RackRoleUpdate(BaseModel):
    name: str | None
    description: str | None


class RackRoleBulkDelete(BaseModel):
    ids: List[int]


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


class RackUpdate(BaseModel):
    name: str | None
    description: str | None
    facility_id: str | None
    site_id: int | None
    location_id: int | None
    device_ids: List[int] | None
    status: constraints.RACK_STATUS | None
    serial_num: List[str] | None
    asset_tag: str | None


class RackBulkUpdate(BaseModel):
    ids: List[str]
    description: str | None
    site_id: int | None
    location_id: int | None
    status: constraints.RACK_STATUS | None


class RackBulkDelete(BaseModel):
    ids: List[int]


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


class ManufacturerUpdate(BaseModel):
    name: str | None
    description: str | None
    device_type_ids: int | List[int] | None

    @validator("device_type_ids")
    def id_trans(cls, v):
        v = items_to_list(v)
        return v


class ManufacturerBulkUpdate(BaseModel):
    ids: List[int]
    description: str | None


class ManufacturerBulkDelete(BaseModel):
    ids: List[int]


class DeviceTypeCreate(BaseModel):
    name: str | None
    description: str | None
    manufacturer_id: int | None
    u_height: float = Field(default=1.0)
    is_full_depth: bool = True
    front_image: UUID4 | None
    rear_image: UUID4 | None


class DeviceTypeQuery(BaseQuery):
    pass


class DeviceTypeUpdate(BaseModel):
    name: str | None
    description: str | None
    manufacturer_id: int | None
    u_height: float | None
    is_full_depth: bool | None
    front_image: UUID4 | None
    rear_image: UUID4 | None


class DeviceTypeBulkUpdate(BaseModel):
    ids: list[int]
    manufacturer_id: int | None
    u_height: float | None
    is_full_depth: bool | None


class DeviceTypeBulkDelete(BaseModel):
    ids: list[int]


class DeviceRoleCreate(BaseModel):
    name: str | None
    description: str | None
    vm_role: bool = False


class DeviceRoleQuery(BaseQuery):
    pass


class DeviceRoleUpdate(BaseModel):
    name: str | None
    description: str | None
    vm_role: bool | None


class DeviceRoleBulkUpdate(BaseModel):
    ids: list[int]
    vm_role: bool
    description: str | None


class DeviceRoleBulkDelete(BaseModel):
    ids: list[int]


class PlatformCreate(BaseModel):
    name: str
    description: str | None
    netdev_platform: constraints.NETDEV_PLATFORM | None


class PlatformQuery(BaseQuery):
    pass


class PlatformUpdate(BaseModel):
    name: str | None
    description: str | None
    netdev_platform: constraints.NETDEV_PLATFORM | None


class PlatformBulkUpdate(BaseModel):
    ids: List[int]
    netdev_platform: constraints.NETDEV_PLATFORM


class PlatformBulkDelete(BaseModel):
    ids: List[int]


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


class InterfaceBulkCreate(BaseModel):
    pass


class InterfaceQuery(BaseQuery):
    pass


class InterfaceUpdate(BaseModel):
    name: str | None
    description: str | None
    if_index: int | None
    speed: int | None
    model: constraints.INTERFACE_MODE = Field(default="access")
    mtu: int | None = Field(default=1500)
    enabled: bool | None = Field(default=True)
    device_id: int | None
    lag_interface_id: int | None
    parent_interface_id: int | None
    vrf_id: int | None
    vlan_id: int | None


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


class InterfaceBulkDelete(BaseModel):
    ids: List[int]
