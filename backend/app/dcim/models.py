from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, UniqueConstraint, func, select
from sqlalchemy.dialects.postgresql import MACADDR
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from app.consts import APMode, APStatus, DeviceStatus, EntityPhysicalClass, InterfaceAdminStatus, RackStatus
from app.db.database import Base
from app.db.db_types import IPvAnyAddress, PgIpAddress, i18n_name, int_pk
from app.db.mixins import AuditLogMixin, AuditTimeMixin

if TYPE_CHECKING:
    from app.db import VLAN, VRF, DeviceRole, IPAddress, Location, RackRole, Site

__all__ = ("Rack", "Vendor", "DeviceType", "Platform", "Device", "Interface", "DeviceEntity", "DeviceGroup", "AP")


class Rack(Base, AuditLogMixin):
    __tablename__ = "rack"
    __visible_name__ = {"en_US": "Rack", "zh_CN": "机柜"}
    __search_fields__ = {"name", "asset_tag", "serial_num"}
    id: Mapped[int_pk]
    name: Mapped[str]
    status: Mapped[RackStatus] = mapped_column(ChoiceType(RackStatus))
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


class Vendor(Base, AuditLogMixin):
    __tablename__ = "vendor"
    __visible_name__ = {"en_US": "Vendor", "zh_CN": "厂商"}
    __i18n_fields__ = {"name"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)


class DeviceType(Base, AuditLogMixin):
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
    vendor: Mapped["Vendor"] = relationship(backref="device_type", passive_deletes=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(backref="device_type")


class Platform(Base, AuditLogMixin):
    __tablename__ = "platform"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    netmiko_driver: Mapped[str | None]


class Device(Base, AuditLogMixin):
    __tablename__ = "device"
    __visible_name__ = {"en_US": "Device", "zh_CN": "设备"}
    __table_args__ = (UniqueConstraint("rack_id", "position"),)
    __search_fields__ = {"name", "management_ipv4", "management_ipv6", "serial_num", "oob_ip"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(index=True)
    management_ipv4: Mapped[IPv4Address | None] = mapped_column(PgIpAddress, index=True, nullable=True)
    management_ipv6: Mapped[IPv6Address | None] = mapped_column(PgIpAddress, index=True, nullable=True)
    oob_ip: Mapped[IPvAnyAddress | None] = mapped_column(PgIpAddress, nullable=True)
    status: Mapped[DeviceStatus] = mapped_column(ChoiceType(DeviceStatus))
    version: Mapped[str | None]
    comments: Mapped[str | None]
    serial_num: Mapped[str | None] = mapped_column(unique=True)
    asset_tag: Mapped[str | None]
    position: Mapped[int | None]
    device_type_id: Mapped[int] = mapped_column(ForeignKey("device_type.id", ondelete="RESTRICT"))
    device_type: Mapped["DeviceType"] = relationship(backref="device", passive_deletes=True)
    device_role_id: Mapped[int] = mapped_column(ForeignKey("device_role.id", ondelete="RESTRICT"))
    device_role: Mapped["DeviceRole"] = relationship(backref="device", passive_deletes=True)
    platform_id: Mapped[int] = mapped_column(comment="redundant platform.id for query performance")
    vendor_id: Mapped[int] = mapped_column(comment="redundant vendor.id for query performance")
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="device", passive_deletes=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location: Mapped["Location"] = relationship(backref="device")
    rack_id: Mapped[int | None] = mapped_column(ForeignKey("rack.id", ondelete="SET NULL"))
    rack: Mapped["Rack"] = relationship(back_populates="device")
    device_group_id: Mapped[int | None] = mapped_column(ForeignKey("device_group.id", ondelete="SET NULL"))
    device_group: Mapped["DeviceGroup"] = relationship(backref="device")
    interface: Mapped[list["Interface"]] = relationship(back_populates="device", passive_deletes=True)
    device_entity: Mapped[list["DeviceEntity"]] = relationship(back_populates="device")


class AP(Base, AuditTimeMixin):
    __tablename__ = "ap"
    __visible_name__ = {"en_US": "AccessPoint", "zh_CN": "无线AP"}
    __search_fields__ = {"name", "ip"}
    __table_args__ = (UniqueConstraint("site_id", "name"),)
    id: Mapped[int_pk]
    name: Mapped[str]
    status: Mapped[APStatus] = mapped_column(ChoiceType(APStatus))
    mode: Mapped[APMode] = mapped_column(ChoiceType(APMode))
    mac_address: Mapped[str] = mapped_column(MACADDR)
    serial_num: Mapped[str | None] = mapped_column(unique=True)
    asset_tag: Mapped[str | None]
    device_type_id: Mapped[int] = mapped_column(ForeignKey("device_type.id", ondelete="RESTRICT"))
    device_type: Mapped["DeviceType"] = relationship(backref="ap")
    ap_group: Mapped[str | None]
    management_ipv4: Mapped[IPv4Address | None] = mapped_column(PgIpAddress, index=True)
    management_ipv6: Mapped[IPv6Address | None] = mapped_column(PgIpAddress, index=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="RESTRICT"))
    site: Mapped["Site"] = relationship(backref="ap")
    location_id: Mapped[int | None] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location: Mapped["Location"] = relationship(backref="ap")
    interface_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface: Mapped["Interface"] = relationship(back_populates="ap")


class DeviceEntity(Base, AuditLogMixin):
    __tablename__ = "device_entity"
    __visible_name__ = {"en_US": "Device Entity", "zh_CN": "设备实体"}
    __search_fields__ = {"serial_num"}
    __table_args__ = (UniqueConstraint("id", "index"),)
    id: Mapped[int_pk]
    index: Mapped[str]
    entity_class: Mapped[EntityPhysicalClass] = mapped_column(ChoiceType(EntityPhysicalClass))
    hardware_version: Mapped[str | None]
    software_version: Mapped[str | None]
    serial_num: Mapped[str | None]
    module_name: Mapped[str | None]
    asset_id: Mapped[str | None]
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
    admin_state: Mapped[InterfaceAdminStatus] = mapped_column(ChoiceType(InterfaceAdminStatus))
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
    vrf: Mapped["VRF"] = relationship(backref="interface")
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlan.id", ondelete="SET NULL"))
    vlan: Mapped["VLAN"] = relationship(backref="interface")
    ip_address: Mapped[list["IPAddress"]] = relationship(back_populates="interface")
    ap: Mapped["AP"] = relationship(back_populates="interface", uselist=False)


class DeviceGroup(Base, AuditLogMixin):
    __tablename__ = "device_group"
    __visible_name__ = {"en_US": "Device Group", "zh_CN": "设备组"}
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str | None]


Rack.device_count = column_property(
    select(func.count(Device.id)).where(Device.rack_id == Rack.id).correlate_except(Rack).scalar_subquery(),
    deferred=True,
)
Vendor.device_type_count = column_property(
    select(func.count(DeviceType.id))
    .where(DeviceType.vendor_id == Vendor.id)
    .correlate_except(Vendor)
    .scalar_subquery(),
    deferred=True,
)
Vendor.device_count = column_property(
    select(func.count(Device.id)).where(Device.vendor_id == Vendor.id).correlate_except(Vendor).scalar_subquery(),
    deferred=True,
)
DeviceType.device_count = column_property(
    select(func.count(Device.id))
    .where(Device.device_type_id == DeviceType.id)
    .correlate_except(DeviceType)
    .scalar_subquery(),
    deferred=True,
)
Platform.device_count = column_property(
    select(func.count(Device.id)).where(Device.platform_id == Platform.id).correlate_except(Platform).scalar_subquery(),
    deferred=True,
)
Platform.device_type_count = column_property(
    select(func.count(DeviceType.id))
    .where(DeviceType.platform_id == Platform.id)
    .correlate_except(Platform)
    .scalar_subquery(),
    deferred=True,
)
Device.interface_count = column_property(
    select(func.count(Interface.id)).where(Interface.device_id == Device.id).correlate_except(Device).scalar_subquery(),
    deferred=True,
)
Device.device_entity_count = column_property(
    select(func.count(DeviceEntity.id))
    .where(DeviceEntity.device_id == Device.id)
    .correlate_except(Device)
    .scalar_subquery(),
    deferred=True,
)
DeviceGroup.device_count = column_property(
    select(func.count(Device.id))
    .where(Device.device_group_id == DeviceGroup.id)
    .correlate_except(DeviceGroup)
    .scalar_subquery(),
    deferred=True,
)
