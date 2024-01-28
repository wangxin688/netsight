from sqlalchemy.orm import Mapped, mapped_column

from src.db._types import i18n_name, int_pk
from src.db.base import Base
from src.db.mixins import AuditUserMixin

__all__ = ("RackRole", "DeviceRole", "IPRole", "CircuitType")


class RackRole(Base, AuditUserMixin):
    __tablename__ = "rack_role"
    __visible_name__ = {"en_US": "Rack Role", "zh_CN": "机柜角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]


class DeviceRole(Base, AuditUserMixin):
    __tablename__ = "device_role"
    __visible_name__ = {"en_US": "Device Role", "zh_CN": "设备角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]


class IPRole(Base, AuditUserMixin):
    __tablename__ = "ip_role"
    __visible_name__ = {"en_US": "IP Role", "zh_CN": "IP角色"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]


class CircuitType(Base, AuditUserMixin):
    __tablename__ = "circuit_type"
    __visible_name__ = {"en_US": "Circuit Type", "zh_CN": "线路类型"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
