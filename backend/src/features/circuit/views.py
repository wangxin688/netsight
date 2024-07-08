from sqladmin import ModelView

from src.features.circuit.models import ISP, Circuit


class CircuitView(ModelView, model=Circuit):
    category = "Circuit"
    name = "Circuit"
    name_plural = "Circuits"


class ISPView(ModelView, model=ISP):
    category = "Circuit"
    name = "ISP"
    name_plural = "ISPs"
