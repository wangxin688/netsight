from sqladmin import ModelView

from src.features.dcim import models


class DeviceView(ModelView, model=models.Device):
    category = "DCIM"

    name = "Device"
    name_plural = "Devices"
    column_list = [
        models.Device.name,
        models.Device.device_type,
        models.Device.device_role,
        models.Device.site,
        models.Device.location,
        models.Device.status,
        models.Device.created_at,
        models.Device.updated_at,
    ]
    column_searchable_list = [models.Device.name]
    column_filters = [models.Device.device_type, models.Device.device_role, models.Device.site, models.Device.location]
