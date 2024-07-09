from sqladmin import ModelView

from src.features.circuit.models import ISP, Circuit


class CircuitView(ModelView, model=Circuit):
    category = "Circuit"
    name = "Circuit"
    name_plural = "Circuits"

    icon = "fa-solid fa-arrow-down-up-across-line"

    column_list = [
        Circuit.name,
        Circuit.cid,
        Circuit.circuit_type,
        Circuit.isp,
        Circuit.site_a,
        Circuit.device_a,
        Circuit.interface_a,
        Circuit.site_z,
        Circuit.device_z,
        Circuit.interface_z,
        Circuit.created_at,
        Circuit.updated_at,
    ]


class ISPView(ModelView, model=ISP):
    category = "Circuit"
    name = "ISP"
    name_plural = "ISPs"

    icon = "fa-solid fa-industry"

    column_list = [ISP.name, ISP.noc_contact, ISP.admin_contact, ISP.created_at, ISP.updated_at]
