from typing import List

from fastapi import Query
from pydantic import Field
from pydantic.dataclasses import dataclass

from src.api.base import BaseModel, BaseQuery
from src.api.dcim import constraints


class RegionBase(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None

    class Config:
        orm_mode = True


class Region(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    parent_id: int | None

    class Config:
        orm_mode = True


class SiteBase(BaseModel):
    id: int
    name: str
    site_code: str
    status: str

    class Config:
        orm_mode = True


class Site(BaseModel):
    id: int
    name: str
    site_code: str
    status: str
    dcim_region: RegionBase | None
    facility: str | None


class Location(BaseModel):
    pass


class LocationBase(BaseModel):
    pass


class Rack(BaseModel):
    pass


class RackBase(BaseModel):
    pass


class RackRole(BaseModel):
    pass


class RackRoleBase(BaseModel):
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


class Cable(BaseModel):
    pass


class CableBase(BaseModel):
    pass


class CablePath(BaseModel):
    pass


class CablePathBase(BaseModel):
    pass


class CableTermination(BaseModel):
    pass


class CableTerminationBase(BaseModel):
    pass


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
    pass


class LocationUpdate(BaseModel):
    pass


@dataclass()
class LocationQuery(BaseQuery):
    pass


class RackRoleCreate(BaseModel):
    pass


class RackRoleUpdate(BaseModel):
    pass


@dataclass()
class RackRoleQuery(BaseQuery):
    pass


class RackCreate(BaseModel):
    pass


class RackUpdate(BaseModel):
    pass


@dataclass()
class RackQuery(BaseQuery):
    pass


class ManufacturerCreate(BaseModel):
    pass


class ManufacturerUpdate(BaseModel):
    pass


@dataclass()
class ManufacturerQuery(BaseQuery):
    pass


class DeviceTypeCreate(BaseModel):
    pass


class DeviceTypeUpdate(BaseModel):
    pass


@dataclass()
class DeviceTypeQuery(BaseQuery):
    pass


class DeviceRoleCreate(BaseModel):
    pass


class DeviceRoleUpdate(BaseModel):
    pass


@dataclass()
class DeviceRoleQuery(BaseQuery):
    pass


class InterfaceCreate(BaseModel):
    pass


class InterfaceUpdate(BaseModel):
    pass


@dataclass
class InterfaceQuery(BaseQuery):
    pass


class CableCreate(BaseModel):
    pass


class CableUpdate(BaseModel):
    pass


@dataclass()
class CableQuery(BaseModel):
    pass


class CablePathCreate(BaseModel):
    pass


class CablePathUpdate(BaseModel):
    pass


@dataclass()
class CablePathQuery(BaseQuery):
    pass


class CableTerminationCreate(BaseModel):
    pass


class CableTerminationUpdate(BaseModel):
    pass


@dataclass()
class CableTerminationQuery(BaseQuery):
    pass
