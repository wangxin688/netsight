from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from src.core.database.base import Base
from src.core.database.mixins import AuditUserMixin
from src.core.database.types import i18n_name, int_pk

if TYPE_CHECKING:
    from src.features.circuit.models import Circuit
    from src.features.ipam.models import VLAN, Prefix

__all__ = ("DeviceRole", "IPRole", "CircuitType", "Platform", "Manufacturer", "DeviceType")


class DeviceRole(Base, AuditUserMixin):
    __tablename__ = "device_role"
    __visible_name__ = {"en_US": "Device Role", "zh_CN": "设备角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    priority: Mapped[int]
    abbreviation: Mapped[str | None]
    description: Mapped[str | None]


class IPRole(Base, AuditUserMixin):
    __tablename__ = "ip_role"
    __visible_name__ = {"en_US": "IP Role", "zh_CN": "IP角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    vlan: Mapped[list["VLAN"]] = relationship(back_populates="role")
    prefix: Mapped[list["Prefix"]] = relationship(back_populates="role")


class CircuitType(Base, AuditUserMixin):
    __tablename__ = "circuit_type"
    __visible_name__ = {"en_US": "Circuit Type", "zh_CN": "线路类型"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    circuit: Mapped[list["Circuit"]] = relationship(back_populates="circuit_type")


class Platform(Base, AuditUserMixin):
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
            select(func.count(DeviceType.id)).where(DeviceType.platform_id == cls.id).scalar_subquery(),
            deferred=True,
        )


class Manufacturer(Base, AuditUserMixin):
    __tablename__ = "manufacturer"
    __visible_name__ = {"en_US": "Manufacturer", "zh_CN": "厂商"}
    __i18n_fields__ = {"name"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)

    if TYPE_CHECKING:
        device_type_count: Mapped[int]
        device_count: Mapped[int]

    @classmethod
    def __declare_last__(cls) -> None:
        from sqlalchemy import func, select

        from src.features.dcim.models import Device

        cls.device_count = column_property(
            select(func.count(Device.id)).where(Device.manufacturer_id == cls.id).scalar_subquery(),
            deferred=True,
        )
        cls.device_type_count = column_property(
            select(func.count(DeviceType.id))
            .where(DeviceType.manufacturer_id == Manufacturer.id)
            .correlate_except(Manufacturer)
            .scalar_subquery(),
            deferred=True,
        )


class DeviceType(Base, AuditUserMixin):
    __tablename__ = "device_type"
    __visible_name__ = {"en_US": "Device Type", "zh_CN": "设备型号"}
    __table_args__ = (UniqueConstraint("manufacturer_id", "name"),)
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    snmp_sysobjectid: Mapped[str]
    u_height: Mapped[float] = mapped_column(Float, server_default="1.0")
    front_image: Mapped[str | None]
    rear_image: Mapped[str | None]
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id", ondelete="RESTRICT"))
    manufacturer: Mapped["Manufacturer"] = relationship(backref="device_type", passive_deletes=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(backref="device_type")

    if TYPE_CHECKING:
        device_count: Mapped[int]

    @classmethod
    def __declare_last__(cls) -> None:
        from sqlalchemy import func, select

        from src.features.dcim.models import Device

        cls.device_count = column_property(
            select(func.count(Device.id)).where(Device.device_type_id == cls.id).scalar_subquery(),
            deferred=True,
        )
