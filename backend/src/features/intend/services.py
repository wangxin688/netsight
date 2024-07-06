from src.core.repositories import BaseRepository
from src.features.intend import models, schemas

__all__ = (
    "device_role_service",
    "device_type_service",
    "platform_service",
    "circuit_type_service",
    "manufacturer_service",
    "ip_role_service",
)


class DeviceRoleService(
    BaseRepository[models.DeviceRole, schemas.DeviceRoleCreate, schemas.DeviceRoleUpdate, schemas.DeviceRoleQuery]
): ...


class DeviceTypeService(
    BaseRepository[models.DeviceType, schemas.DeviceTypeCreate, schemas.DeviceTypeUpdate, schemas.DeviceTypeQuery]
): ...


class PlatformService(
    BaseRepository[models.Platform, schemas.PlatformCreate, schemas.PlatformUpdate, schemas.PlatformQuery]
): ...


class CircuitTypeService(
    BaseRepository[models.CircuitType, schemas.CircuitTypeCreate, schemas.CircuitTypeUpdate, schemas.CircuitTypeQuery]
): ...


class ManufacturerService(
    BaseRepository[
        models.Manufacturer, schemas.ManufacturerCreate, schemas.ManufacturerUpdate, schemas.ManufacturerQuery
    ]
): ...


class IPRoleService(BaseRepository[models.IPRole, schemas.IPRoleCreate, schemas.IPRoleUpdate, schemas.IPRoleQuery]): ...


device_role_service = DeviceRoleService(models.DeviceRole)
device_type_service = DeviceTypeService(models.DeviceType)
platform_service = PlatformService(models.Platform)
circuit_type_service = CircuitTypeService(models.CircuitType)
manufacturer_service = ManufacturerService(models.Manufacturer)
ip_role_service = IPRoleService(models.IPRole)
