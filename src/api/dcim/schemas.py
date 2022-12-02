from api.base import BaseModel


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
    pass


class Site(BaseModel):
    pass


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


class RegionQuery(BaseModel):
    pass


class SiteCreate(BaseModel):
    pass


class SiteUpdate(BaseModel):
    pass


class SiteQuery(BaseModel):
    pass


class LocationCreate(BaseModel):
    pass


class LocationUpdate(BaseModel):
    pass


class LocationQuery(BaseModel):
    pass


class RackRoleCreate(BaseModel):
    pass


class RackRoleUpdate(BaseModel):
    pass


class RackRoleQuery(BaseModel):
    pass


class RackCreate(BaseModel):
    pass


class RackUpdate(BaseModel):
    pass


class RackQuery(BaseModel):
    pass


class ManufacturerCreate(BaseModel):
    pass


class ManufacturerUpdate(BaseModel):
    pass


class ManufacturerQuery(BaseModel):
    pass


class DeviceTypeCreate(BaseModel):
    pass


class DeviceTypeUpdate(BaseModel):
    pass


class DeviceTypeQuery(BaseModel):
    pass


class DeviceRoleCreate(BaseModel):
    pass


class DeviceRoleUpdate(BaseModel):
    pass


class DeviceRoleQuery(BaseModel):
    pass


class InterfaceCreate(BaseModel):
    pass


class InterfaceUpdate(BaseModel):
    pass


class InterfaceQuery(BaseModel):
    pass


class CableCreate(BaseModel):
    pass


class CableUpdate(BaseModel):
    pass


class CableQuery(BaseModel):
    pass


class CablePathCreate(BaseModel):
    pass


class CablePathUpdate(BaseModel):
    pass


class CablePathQuery(BaseModel):
    pass


class CableTerminationCreate(BaseModel):
    pass


class CableTerminationUpdate(BaseModel):
    pass


class CableTerminationQuery(BaseModel):
    pass
