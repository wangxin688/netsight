from pydantic.dataclasses import dataclass

from src.api.base import BaseModel, BaseQuery


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
    pass


class RegionUpdate(BaseModel):
    pass


@dataclass()
class RegionQuery(BaseQuery):
    pass


class SiteCreate(BaseModel):
    pass


class SiteUpdate(BaseModel):
    pass


@dataclass()
class SiteQuery(BaseQuery):
    pass


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
