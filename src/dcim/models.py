from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db._types import IntegerEnum, i18n_name, int_pk
from src.db.base import Base
from src.db.mixins import AuditLogMixin, AuditTimeMixin, AuditUserMixin
from src.enums import DeviceStatus, InterfaceAdminStatus, RackStatus

if TYPE_CHECKING:
    from src.arch.models import DeviceRole, RackRole
    from src.ipam.models import VLAN, VRF, IPAddress
    from src.org.models import Location, Site


class Rack(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "rack"
    __visible_name__ = {"en_US": "Rack", "zh_CN": "机柜"}
    __search_fields__ = {"name", "asset_tag", "serial_num"}
    id: Mapped[int_pk]
    name: Mapped[str]
    status: Mapped[RackStatus] = mapped_column(IntegerEnum(RackStatus))
    serial_num: Mapped[str | None] = mapped_column(unique=True)
    asset_tag: Mapped[str | None] = mapped_column(unique=True)
    u_width: Mapped[float | None]
    u_height: Mapped[float | None]
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="rack", passive_deletes=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location: Mapped["Location"] = relationship(backref="rack")
    rack_role_id: Mapped[int | str] = mapped_column(ForeignKey("rack_role.id", ondelete="RESTRICT"))
    rack_role: Mapped["RackRole"] = relationship("RackRole", backref="rack")
    device: Mapped[list["Device"]] = relationship(back_populates="rack")


class Vendor(Base, AuditTimeMixin, AuditUserMixin):
    __tablename__ = ""
    __visible_name__ = {"en_US": "Vendor", "zh_CN": "厂商"}
    __i18n_fields__ = {"name"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    device_type: Mapped[list["DeviceType"]] = relationship(back_populates="vendor")
    platform: Mapped[list["Platform"]] = relationship(back_populates="vendor")


class DeviceType(Base, AuditTimeMixin, AuditUserMixin):
    __tablename__ = "device_type"
    __visible_name__ = {"en_US": "Device Type", "zh_CN": "设备型号"}
    __table_args__ = (UniqueConstraint("vendor_id", "name"),)
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    snmp_sysobjectid: Mapped[str]
    u_height: Mapped[float] = mapped_column(Float, server_default="1.0")
    front_image: Mapped[str | None]
    rear_image: Mapped[str | None]
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id", ondelete="RESTRICT"))
    vendor: Mapped["Vendor"] = relationship(back_populates="device_type", passive_deletes=True)


class Platform(Base, AuditTimeMixin, AuditUserMixin):
    __tablename__ = "platform"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    netmiko_driver: Mapped[str | None]
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id", ondelete="RESTRICT"))
    vendor: Mapped[Vendor] = relationship(back_populates="platform", passive_deletes=True)


class Device(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "device"
    __visible_name__ = {"en_US": "Device", "zh_CN": "设备"}
    __table_args__ = (UniqueConstraint("rack_id", "position"),)
    __search_fields__ = {"name", "management_ipv4", "management_ipv6", "serial_num"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(index=True)
    management_ipv4: Mapped[str | None] = mapped_column(INET, index=True)
    management_ipv6: Mapped[str | None] = mapped_column(INET, index=True)
    status: Mapped[DeviceStatus] = mapped_column(IntegerEnum(DeviceStatus))
    version: Mapped[str | None]
    comments: Mapped[str | None]
    serial_num: Mapped[str | None] = mapped_column(unique=True)
    asset_tag: Mapped[str | None]
    device_type_id: Mapped[int] = mapped_column(ForeignKey("device_type.id", ondelete="RESTRICT"))
    device_type: Mapped["DeviceType"] = relationship(backref="device", passive_deletes=True)
    device_role_id: Mapped[int] = mapped_column(ForeignKey("device_role.id", ondelete="RESTRICT"))
    device_role: Mapped["DeviceRole"] = relationship(back_populates="device", passive_deletes=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="CASCADE"))
    platform: Mapped["Platform"] = relationship(backref="device", passive_deletes=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(back_populates="device", passive_deletes=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location: Mapped["Location"] = relationship(back_populates="device")
    rack_id: Mapped[int | None] = mapped_column(ForeignKey("rack.id", ondelete="SET NULL"))
    rack: Mapped["Rack"] = relationship(back_populates="device")
    device_group_id: Mapped[int | None] = mapped_column(ForeignKey("device_group.id", ondelete="SET NULL"))
    device_group: Mapped["DeviceGroup"] = relationship(backref="device")
    interface: Mapped[list["Interface"]] = relationship(back_populates="device", passive_deletes=True)
    device_entity: Mapped[list["DeviceEntity"]] = relationship(back_populates="device")


class DeviceEntity(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "device_entity"
    __visible_name__ = {"en_US": "Device Entity", "zh_CN": "设备实体"}
    __search_fields__ = {"serial_num"}
    __table_args__ = (UniqueConstraint("id", "index"),)
    id: Mapped[int_pk]
    index: Mapped[int]
    entity_class: Mapped[int]
    hardware_version: Mapped[str | None]
    software_version: Mapped[str | None]
    serial_num: Mapped[str | None]
    model_name: Mapped[str | None]
    asset_id: Mapped[str | None]
    serial: Mapped[str | None]
    order: Mapped[int]
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))
    device: Mapped["Device"] = relationship(back_populates="device_entity", passive_deletes=True)


class Interface(Base):
    __tablename__ = "interface"
    __table_args__ = (UniqueConstraint("device_id", "name"),)
    __visible_name__ = {"en_US": "Interface", "zh_CN": "interface"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    if_index: Mapped[int | None]
    speed: Mapped[int | None]
    mode: Mapped[str]
    interface_type: Mapped[str | None]
    mtu: Mapped[int | None]
    admin_state: Mapped[InterfaceAdminStatus] = mapped_column(IntegerEnum(InterfaceAdminStatus))
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))
    device: Mapped["Device"] = relationship(back_populates="interface")
    lag_interface_id: Mapped[int | None] = mapped_column(
        ForeignKey(id, ondelete="CASCADE"),
        comment="port channel or eth-trunk",
    )
    lag_member: Mapped[list["Interface"]] = relationship(
        foreign_keys=[lag_interface_id],
        lazy="selectin",
        join_depth=1,
        cascade="all, delete-orphan",
    )
    parent_interface_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(id, ondelete="CASCADE"),
        comment="child interface, like g0/0/1.0",
    )
    children_interface: Mapped[list["Interface"]] = relationship(
        foreign_keys=[parent_interface_id], lazy="selectin", join_depth=1, cascade="all, delete-orphan"
    )
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship("VRF", backref="interface")
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlan.id", ondelete="SET NULL"))
    vlan: Mapped["VLAN"] = relationship(backref="interface")
    ip_address: Mapped[list["IPAddress"]] = relationship("IPAddress", back_populates="interface")


class DeviceGroup(Base, AuditTimeMixin, AuditUserMixin):
    __tablename__ = "device_group"
    __visible_name__ = {"en_US": "Device Group", "zh_CN": "设备组"}
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str | None]
