from sqladmin import ModelView

from src.features.intend import models


class DeviceTypeView(ModelView, model=models.DeviceType):
    name = "Device Type"
    name_plural = "Device Types"


class PlatformView(ModelView, model=models.Platform):
    category = "Intend"

    name = "Platform"
    name_plural = "Platforms"


class DeviceRoleView(ModelView, model=models.DeviceRole):
    category = "Intend"

    name = "Device Role"
    name_plural = "Device Roles"


class CircuitTypeView(ModelView, model=models.CircuitType):
    category = "Intend"

    name = "Circuit Type"
    name_plural = "Circuit Types"


class IPRoleView(ModelView, model=models.IPRole):
    category = "Intend"

    name = "IP Role"
    name_plural = "IP Roles"


class ManufacturerView(ModelView, model=models.Manufacturer):
    category = "Intend"
    name = "Manufacturer"
    name_plural = "Manufacturers"
