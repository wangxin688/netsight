from sqladmin import ModelView

from src.features.intend import models


class DeviceTypeView(ModelView, model=models.DeviceType):
    category = "Intend"
    name = "Device Type"
    name_plural = "Device Types"

    icon = "fa-solid fa-hard-drive"

    column_list = [
        models.DeviceType.name,
        models.DeviceType.u_height,
        models.DeviceType.snmp_sysobjectid,
        models.DeviceType.manufacturer,
        models.DeviceType.platform,
        models.DeviceType.created_at,
        models.DeviceType.updated_at,
    ]


class PlatformView(ModelView, model=models.Platform):
    category = "Intend"

    name = "Platform"
    name_plural = "Platforms"
    icon = "fa-solid fa-shredder"

    column_list = [
        models.Platform.name,
        models.Platform.slug,
        models.Platform.description,
        models.Platform.netmiko_driver,
        models.Platform.created_at,
        models.Platform.updated_at,
    ]


class DeviceRoleView(ModelView, model=models.DeviceRole):
    category = "Intend"

    name = "Device Role"
    name_plural = "Device Roles"
    icon = "fa-solid fa-tablet-rugged"

    column_list = [
        models.DeviceRole.name,
        models.DeviceRole.priority,
        models.DeviceRole.abbreviation,
        models.DeviceRole.description,
        models.DeviceRole.created_at,
        models.DeviceRole.updated_at,
    ]


class CircuitTypeView(ModelView, model=models.CircuitType):
    category = "Intend"

    name = "Circuit Type"
    name_plural = "Circuit Types"
    icon = "fa-sharp fa-solid fa-plug"

    column_list = [
        models.CircuitType.name,
        models.CircuitType.slug,
        models.CircuitType.description,
        models.CircuitType.created_at,
        models.CircuitType.updated_at,
    ]


class IPRoleView(ModelView, model=models.IPRole):
    category = "Intend"

    name = "IP Role"
    name_plural = "IP Roles"

    icon = "fa-solid fa-network-wired"

    column_list = [
        models.IPRole.name,
        models.IPRole.slug,
        models.IPRole.description,
        models.IPRole.created_at,
        models.IPRole.updated_at,
    ]


class ManufacturerView(ModelView, model=models.Manufacturer):
    category = "Intend"
    name = "Manufacturer"
    name_plural = "Manufacturers"

    icon = "fa-solid fa-industry"

    column_list = [
        models.Manufacturer.name,
        models.Manufacturer.slug,
        models.Manufacturer.created_at,
        models.Manufacturer.updated_at,
    ]
