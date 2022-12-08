from typing import List, Literal

from fastapi import Query
from pydantic import Field, validator
from pydantic.dataclasses import dataclass

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


class RegionUpdate(BaseModel):
    name: str | None
    description: str | None
    parent_id: int | None


@dataclass()
class RegionQuery(BaseQuery):
    id: List[int] = Query(default=None)
    name: List[str] | None = Query(default=None)


class RegionBulkOperate(BaseModel):
    action: Literal["update", "delete"]
    region_ids: List[int]
    description: str | None
    parent_id: int | None


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
    time_zone: constraints.ALL_TIME_ZONES
    physical_address: str | None
    shipping_address: str | None
    latitude: float | None
    longitude: float | None
    classification: constraints.SITE_CLASSIFICATIONS | None
    functions: List[str] | None = Field(
        description="a set of tags to mark the function of the sites, e.g.`RD`, `Sales`, `Mixed`"
    )
    contact_ids: List[int] | None


@dataclass()
class SiteQuery(BaseQuery):
    id: List[int] = Query(None)
    name: str = Query(None)
    site_code: str = Query(None)
    status: constraints.SITE_STATUS = Query(None)


class LocationCreate(BaseModel):
    name: str
    description: str | None
    status: constraints.LOCATION_STATUS
    parent_id: int | None
    site_id: int


class LocationUpdate(BaseModel):
    name: str | None
    description: str | None
    parent_id: int | None
    dcim_site_id: int | None


@dataclass()
class LocationQuery(BaseQuery):
    id: List[int] = Query(None)
    name: str = Query(None)
    site_id: int = Query(None)


class RackRoleCreate(BaseModel):
    name: str
    description: str | None


class RackRoleUpdate(BaseModel):
    name: str | None
    description: str | None


@dataclass()
class RackRoleQuery(BaseQuery):
    id: List[int] = Query(None)
    name: str = Query(None)


class RackCreate(BaseModel):
    pass


class RackUpdate(BaseModel):
    pass


@dataclass()
class RackQuery(BaseQuery):
    pass


class ManufacturerCreate(BaseModel):
    name: str
    description: str | None
    device_type_ids: int | List[int] | None

    @validator("device_type_ids")
    def id_trans(cls, v):
        v = items_to_list(v)
        return v


class ManufacturerUpdate(BaseModel):
    name: str | None
    description: str | None
    device_type_ids: int | List[int] | None

    @validator("device_type_ids")
    def id_trans(cls, v):
        v = items_to_list(v)
        return v


@dataclass()
class ManufacturerQuery(BaseQuery):
    pass


class DeviceTypeCreate(BaseModel):
    name: str | None
    description: str | None
    manufacturer_id: int | None
    model: str
    u_height: float = Field(default=1.0)
    is_full_depth: bool = True


class DeviceTypeUpdate(BaseModel):
    name: str | None
    description: str | None
    manufacturer_id: int | None
    model: str | None
    u_height: float | None
    is_full_depth: bool | None


@dataclass()
class DeviceTypeQuery(BaseQuery):
    pass


class DeviceRoleCreate(BaseModel):
    name: str | None
    description: str | None
    vm_role: bool = False


class DeviceRoleUpdate(BaseModel):
    name: str | None
    description: str | None
    vm_role: bool | None


@dataclass()
class DeviceRoleQuery(BaseQuery):
    pass


class PlatformCreate(BaseModel):
    name: str
    description: str | None
    napalm_driver: str | None
    napalm_args: dict | None


class PlatformUpdate(BaseModel):
    name: str | None
    description: str | None
    napalm_driver: str | None
    napalm_args: dict | None


@dataclass()
class PlatformQuery(BaseQuery):
    pass


class InterfaceCreate(BaseModel):
    name: str
    description: str | None
    if_index: int | None
    speed: int | None
    model: constraints.INTERFACE_MODE = Field(default="access")
    mtu: int | None = Field(default=1500)
    enabled: bool | None = Field(default=True)
    device_id: int


class InterfaceUpdate(BaseModel):
    name: str | None
    description: str | None
    if_index: int | None
    speed: int | None
    model: constraints.INTERFACE_MODE = Field(default="access")
    mtu: int | None = Field(default=1500)
    enabled: bool | None = Field(default=True)
    device_id: int | None


@dataclass()
class InterfaceQuery(BaseQuery):
    pass
