from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TEXT, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from src.core.database import Base
from src.core.database.mixins import AuditLogMixin, AuditTimeMixin, AuditUserMixin
from src.core.database.types import DateTimeTZ, PgIpAddress, int_pk
from src.features._types import IPvAnyAddress
from src.features.consts import APMode, DeviceEquipmentType, DeviceStatus, InterfaceAdminStatus

if TYPE_CHECKING:
    from src.features.intend.models import DeviceRole, DeviceType, Manufacturer, Platform
    from src.features.ipam.models import VLAN, IPAddress
    from src.features.org.models import Location, Site

__all__ = ("Device", "DeviceModule", "DeviceStack", "DeviceConfig", "Interface", "LldpNeighbor")


class Device(Base, AuditUserMixin, AuditLogMixin):
    # make sure device is management by logic in dcim.views. if device is stacked
    #  members should be added and treated as stacked for this master device
    __tablename__ = "device"
    __visible_name__ = {"en_US": "Device", "zh_CN": "设备"}
    __search_fields__ = {"name", "management_ipv4", "management_ipv6", "serial_num", "oob_ip"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(index=True)
    management_ip: Mapped[IPvAnyAddress] = mapped_column(PgIpAddress, index=True)
    oob_ip: Mapped[IPvAnyAddress | None] = mapped_column(PgIpAddress, nullable=True)
    status: Mapped[DeviceStatus] = mapped_column(ChoiceType(DeviceStatus, impl=String()))
    software_version: Mapped[str | None]
    software_patch: Mapped[str | None]
    comments: Mapped[str | None]
    serial_number: Mapped[str | None] = mapped_column(unique=True)  # master
    asset_tag: Mapped[str | None]
    device_type_id: Mapped[int] = mapped_column(ForeignKey("device_type.id", ondelete="RESTRICT"))
    device_type: Mapped["DeviceType"] = relationship(backref="device", passive_deletes=True)
    device_role_id: Mapped[int] = mapped_column(ForeignKey("device_role.id", ondelete="RESTRICT"))
    device_role: Mapped["DeviceRole"] = relationship(backref="device", passive_deletes=True)
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platform.id", ondelete="RESTRICT"), comment="redundant platform.id for query performance"
    )
    platform: Mapped["Platform"] = relationship(backref="device", passive_deletes=True)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturer.id", ondelete="RESTRICT"), comment="redundant manufacturer.id for query performance"
    )
    manufacturer: Mapped["Manufacturer"] = relationship(backref="device", passive_deletes=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="device", passive_deletes=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location: Mapped["Location"] = relationship(backref="device")
    interface: Mapped[list["Interface"]] = relationship(back_populates="device", passive_deletes=True)
    module: Mapped[list["DeviceModule"]] = relationship(backref="device")
    stack: Mapped[list["DeviceStack"]] = relationship(backref="device")
    equipment: Mapped[list["DeviceEquipment"]] = relationship(backref="device")

    # these three are only used for AP device role
    associated_wac_ip: Mapped[IPvAnyAddress | None] = mapped_column(PgIpAddress, nullable=True)
    ap_group: Mapped[str | None]
    ap_mode: Mapped[APMode | None] = mapped_column(ChoiceType(APMode, impl=String()), nullable=True)


class DeviceModule(Base, AuditTimeMixin):
    __tablename__ = "module"
    id: Mapped[int_pk]
    name: Mapped[str]  # huawei: module
    description: Mapped[str | None]  # huawei board info
    serial_number: Mapped[str | None] = mapped_column(unique=True)
    part_number: Mapped[str | None]
    hardware_version: Mapped[str | None]
    physical_index: Mapped[int | None]  # cisco physical_index, huawei slot_id
    replaceable: Mapped[bool | None]
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class DeviceStack(Base, AuditTimeMixin):
    __tablename__ = "stack"
    id: Mapped[int_pk]
    role: Mapped[str]
    mac_address: Mapped[str]
    priority: Mapped[int | None]
    device_type: Mapped[str]
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class DeviceEquipment(Base, AuditTimeMixin):
    # device FAN/Power/SFP Module
    __tablename__ = "equipment"
    __visible_name__ = {"en_US": "Equipment", "zh_CN": "Equipment"}
    id: Mapped[int_pk]
    name: Mapped[str]
    eq_type: Mapped[DeviceEquipmentType] = mapped_column(ChoiceType(DeviceEquipmentType, impl=String()))
    description: Mapped[str | None]
    device_type: Mapped[str | None]
    serial_number: Mapped[str | None]
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class DeviceConfig(Base):
    __tablename__ = "device_config"
    __visible_name__ = {"en_US": "Device Config", "zh_CN": "设备配置"}
    id: Mapped[int_pk]
    # if you want to save many history configuration versions, db is not recommended.
    # store content in Object Storage
    # change configuration content to download URL path in db.
    configuration: Mapped[str] = mapped_column(TEXT)
    total_lines: Mapped[int] = mapped_column(default=0, server_default="0")
    lines_added: Mapped[int] = mapped_column(default=0, server_default="0")
    lines_deleted: Mapped[int] = mapped_column(default=0, server_default="0")
    lines_updated: Mapped[int] = mapped_column(default=0, server_default="0")
    md5_checksum: Mapped[str | None]
    created_by: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTimeTZ, default=func.now())
    change_event: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class Interface(Base, AuditTimeMixin):
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
    admin_status: Mapped[InterfaceAdminStatus] = mapped_column(ChoiceType(InterfaceAdminStatus, impl=String()))
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))
    device: Mapped["Device"] = relationship(back_populates="interface")
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlan.id", ondelete="SET NULL"))  # access port only
    vlan: Mapped["VLAN"] = relationship(backref="interface")
    ip_address: Mapped[list["IPAddress"]] = relationship(back_populates="interface")


class LldpNeighbor(Base, AuditTimeMixin):
    __tablename__ = "lldp_neighbor"
    __visible_name__ = {"en_US": "LLDP Neighbor", "zh_CN": "LLDP邻居"}
    id: Mapped[int_pk]
    source_interface_id: Mapped[int] = mapped_column(ForeignKey("interface.id", ondelete="CASCADE"))
    source_interface: Mapped["Interface"] = relationship(backref="source_interface", foreign_keys=[source_interface_id])
    source_device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))
    source_device: Mapped["Device"] = relationship(backref="source_device", foreign_keys=[source_device_id])
    target_interface_id: Mapped[int] = mapped_column(ForeignKey("interface.id", ondelete="CASCADE"))
    target_interface: Mapped["Interface"] = relationship(backref="target_interface", foreign_keys=[target_interface_id])
    target_device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))
    target_device: Mapped["Device"] = relationship(backref="target_device", foreign_keys=[target_device_id])
    link_status: Mapped[str | None]
