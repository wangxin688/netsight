from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from src.core.database.types import i18n_name, int_pk
from src.core.models.base import Base
from src.core.models.mixins import AuditLogMixin

if TYPE_CHECKING:
    from src.features.circuit.models import Circuit
    from src.features.ipam.models import VLAN, Prefix

__all__ = ("RackRole", "DeviceRole", "IPRole", "CircuitType", "Platform")


class RackRole(Base, AuditLogMixin):
    __tablename__ = "rack_role"
    __visible_name__ = {"en_US": "Rack Role", "zh_CN": "机柜角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]


class DeviceRole(Base, AuditLogMixin):
    __tablename__ = "device_role"
    __visible_name__ = {"en_US": "Device Role", "zh_CN": "设备角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    priority: Mapped[int]
    abbreviation: Mapped[str | None]
    description: Mapped[str | None]


class IPRole(Base, AuditLogMixin):
    __tablename__ = "ip_role"
    __visible_name__ = {"en_US": "IP Role", "zh_CN": "IP角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    vlan: Mapped[list["VLAN"]] = relationship(back_populates="role")
    prefix: Mapped[list["Prefix"]] = relationship(back_populates="role")


class CircuitType(Base, AuditLogMixin):
    __tablename__ = "circuit_type"
    __visible_name__ = {"en_US": "Circuit Type", "zh_CN": "线路类型"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    circuit: Mapped[list["Circuit"]] = relationship(back_populates="circuit_type")


class Platform(Base, AuditLogMixin):
    __tablename__ = "platform"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    netmiko_driver: Mapped[str | None]


    if TYPE_CHECKING:
        device_count: Mapped[int]
        device_type_count: Mapped[int]

    @classmethod
    def __declare_last__(cls) -> None:
        from sqlalchemy import func, select

        from src.features.dcim.models import Device, DeviceType

        cls.device_count = column_property(
            select(func.count(Device.id)).where(Device.platform_id == cls.id).scalar_subquery(),
            deferred=True,
        )
        cls.device_type_count = column_property(
            select(func.count(DeviceType.id))
            .where(DeviceType.platform_id == cls.id)
            .scalar_subquery(),
            deferred=True,
        )
