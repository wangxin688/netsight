from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, INET, UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import AuditLogMixin, NameMixin, TimestampMixin

__all__ = (
    "Region",
    "Site",
    "Location",
    "RackRole",
    "Rack",
    "Manufacturer",
    "DeviceType",
    "DeviceRole",
    "Interface",
    "Platform",
)


class Region(Base, NameMixin, AuditLogMixin):
    __tablename__ = "dcim_region"
    __table_args__ = (UniqueConstraint("parent_id", "name"),)
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(id))
    dcim_site = relationship(
        "Site",
        back_populates="dcim_region",
        passive_deletes=True,
    )

    children = relationship(
        "Region",
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )

    def __repr__(self):
        return "Region(name=%r, id=%r, parent_id=%r)" % (
            self.name,
            self.id,
            self.parent_id,
        )


class Site(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "dcim_site"
    id = Column(Integer, primary_key=True)
    site_code = Column(String, unique=True, nullable=False, index=True)
    status = Column(
        ENUM(
            "Active",
            "Retired",
            "Planning",
            "Staged",
            "Canceled",
            "Validated",
            name="site_status",
            create_type=False,
        ),
        nullable=False,
    )
    region_id = Column(
        Integer, ForeignKey("dcim_region.id", ondelete="SET NULL"), nullable=True
    )
    dcim_region = relationship(
        "Region", back_populates="dcim_site", overlaps="dcim_site"
    )
    facility = Column(String, nullable=True)
    ipam_asn = relationship(
        "ASN",
        secondary="dcim_site_asn_link",
        overlaps="dcim_site",
        back_populates="dcim_site",
    )
    time_zone = Column(String, nullable=True)
    physical_address = Column(String, nullable=True)
    shipping_address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    classification = Column(String, nullable=True)
    functions = Column(ARRAY(String, dimensions=1), nullable=True)
    contact = relationship(
        "Contact",
        secondary="dcim_site_contact_link",
        overlaps="dcim_site",
        back_populates="dcim_site",
    )
    dcim_location = relationship(
        "Location",
        back_populates="dcim_site",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_rack = relationship(
        "Rack",
        back_populates="dcim_site",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_device = relationship(
        "Device",
        back_populates="dcim_site",
        cascade="all, delete",
        passive_deletes=True,
    )
    ipam_prefix = relationship(
        "Prefix", back_populates="dcim_site", passive_deletes=True
    )
    ipam_vlan = relationship("VLAN", back_populates="dcim_site", passive_deletes=True)

    circuit_termination = relationship(
        "CircuitTermination", back_populates="dcim_site", passive_deletes=True
    )


class Location(Base, TimestampMixin, AuditLogMixin):
    """a sub location of site, like building, floor, idf, mdf and etc"""

    __tablename__ = "dcim_location"
    __table_args__ = (UniqueConstraint("site_id", "name"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    status = Column(
        ENUM(
            "Active",
            "Retired",
            "Planning",
            "Staged",
            "Canceled",
            "Validated",
            name="location_status",
            create_type=False,
        ),
        nullable=False,
    )
    site_id = Column(Integer, ForeignKey("dcim_site.id", ondelete="CASCADE"))
    dcim_site = relationship(
        "Site", back_populates="dcim_location", overlaps="dcim_location"
    )
    dcim_rack = relationship(
        "Rack",
        back_populates="dcim_location",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_device = relationship(
        "Device",
        back_populates="dcim_location",
        passive_deletes=True,
    )
    parent_id = Column(Integer, ForeignKey(id))
    children = relationship(
        "Location",
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )


class RackRole(Base):
    __tablename__ = "dcim_rack_role"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    dcim_rack = relationship(
        "Rack", back_populates="dcim_rack_role", passive_deletes=True
    )


class Rack(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "dcim_rack"
    id = Column(Integer, primary_key=True)
    facility_id = Column(String, nullable=True)
    site_id = Column(Integer, ForeignKey("dcim_site.id", ondelete="CASCADE"))
    dcim_site = relationship("Site", back_populates="dcim_rack", overlaps="dcim_rack")
    location_id = Column(
        Integer, ForeignKey("dcim_location.id", ondelete="SET NULL"), nullable=True
    )
    dcim_location = relationship(
        "Location", back_populates="dcim_rack", overlaps="dcim_rack"
    )
    dcim_device = relationship(
        "Device",
        back_populates="dcim_rack",
        passive_deletes=True,
    )
    status = Column(
        ENUM(
            "Active",
            "Offline",
            "Staged",
            "Planning",
            name="rack_status",
            create_type=False,
        ),
        nullable=False,
    )
    serial_num = Column(String, nullable=True)
    asset_tag = Column(String, nullable=True, unique=True)
    rack_role_id = Column(
        Integer, ForeignKey("dcim_rack_role.id", ondelete="SET NULL"), nullable=True
    )
    dcim_rack_role = relationship(
        "RackRole", back_populates="dcim_rack", passive_deletes=True
    )
    # TODO: pydantic Rack width and height validator
    width = Column(Integer, nullable=False, comment="Rail-to-rail width")
    u_height = Column(Integer, nullable=False, comment="Height in rack units")
    desc_units = Column(
        Boolean,
        server_default=expression.false(),
        comment="Units are numbered top-to-bottom",
    )
    outer_width = Column(
        Integer, nullable=False, comment="Outer dimension of rack (width)"
    )
    outer_depth = Column(
        Integer, nullable=False, comment="Outer dimension of rack (depth)"
    )
    outer_unit = Column(String, nullable=True)
    comments = Column(Text, nullable=True)


class Manufacturer(Base):
    __tablename__ = "dcim_manufacturer"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    dcim_device_type = relationship(
        "DeviceType",
        back_populates="dcim_manufacturer",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_device = relationship(
        "Device", back_populates="dcim_manufacturer", passive_deletes=True
    )


class DeviceType(Base):
    __tablename__ = "dcim_device_type"
    __table_args__ = (UniqueConstraint("manufacturer_id", "name"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    manufacturer_id = Column(
        Integer, ForeignKey("dcim_manufacturer.id", ondelete="CASCADE")
    )
    dcim_manufacturer = relationship(
        "Manufacturer", back_populates="dcim_device_type", overlaps="dcim_device_type"
    )
    u_height = Column(Float, server_default="1.0")
    is_full_depth = Column(Boolean, server_default=expression.true())
    dcim_device = relationship(
        "Device", back_populates="dcim_device_type", passive_deletes=True
    )
    front_image = Column(UUID(as_uuid=True), nullable=True)
    rear_image = Column(UUID(as_uuid=True), nullable=True)


class DeviceRole(Base):
    __tablename__ = "dcim_device_role"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    vm_role = Column(Boolean, server_default=expression.false())
    dcim_device = relationship(
        "Device", back_populates="dcim_device_role", passive_deletes=True
    )
    server = relationship(
        "Server", back_populates="dcim_device_role", passive_deletes=True
    )


class Platform(Base):
    __tablename__ = "dcim_platform"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    netdev_platform = Column(String, nullable=True)
    dcim_device = relationship(
        "Device", back_populates="dcim_platform", passive_deletes=True
    )
    server = relationship(
        "Server", back_populates="dcim_platform", passive_deletes=True
    )


class Device(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "dcim_device"
    __table_args__ = (UniqueConstraint("rack_id", "position"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    primary_ipv4 = Column(INET, nullable=True, index=True)
    primary_ipv6 = Column(INET, nullable=True, index=True)
    description = Column(String, nullable=True)
    device_type_id = Column(
        Integer, ForeignKey("dcim_device_type.id", ondelete="SET NULL"), nullable=True
    )
    dcim_device_type = relationship(
        "DeviceType", back_populates="dcim_device", overlaps="dcim_device"
    )
    device_role_id = Column(
        Integer, ForeignKey("dcim_device_role.id", ondelete="SET NULL"), nullable=True
    )
    dcim_device_role = relationship(
        "DeviceRole", back_populates="dcim_device", overlaps="dcim_device"
    )
    platform_id = Column(
        Integer, ForeignKey("dcim_platform.id", ondelete="SET NULL"), nullable=True
    )
    dcim_platform = relationship(
        "Platform", back_populates="dcim_device", overlaps="dcim_device"
    )
    site_id = Column(Integer, ForeignKey("dcim_site.id", ondelete="CASCADE"))
    dcim_site = relationship(
        "Site", back_populates="dcim_device", overlaps="dcim_device"
    )
    location_id = Column(
        Integer, ForeignKey("dcim_location.id", ondelete="SET NULL"), nullable=True
    )
    dcim_location = relationship(
        "Location", back_populates="dcim_device", overlaps="dcim_device"
    )
    rack_id = Column(
        Integer, ForeignKey("dcim_rack.id", ondelete="SET NULL"), nullable=True
    )
    dcim_rack = relationship(
        "Rack", back_populates="dcim_device", overlaps="dcim_device"
    )
    manufacturer_id = Column(
        Integer, ForeignKey("dcim_manufacturer.id", ondelete="SET NULL"), nullable=True
    )
    dcim_manufacturer = relationship(
        Manufacturer, back_populates="dcim_device", overlaps="dcim_device"
    )
    position = Column(Float, nullable=True)
    serial_num = Column(String, nullable=True, unique=True)
    asset_tag = Column(String, unique=True, nullable=True)
    status = Column(
        ENUM(
            "Active",
            "Offline",
            "Staged",
            "Planning",
            name="device_status",
            create_type=False,
        ),
        nullable=False,
    )
    cluster_id = Column(
        Integer, ForeignKey("cluster.id", ondelete="SET NULL"), nullable=True
    )
    cluster = relationship(
        "Cluster", back_populates="dcim_device", overlaps="dcim_device"
    )
    comments = Column(Text, nullable=True)
    dcim_interface = relationship(
        "Interface",
        back_populates="dcim_device",
        cascade="all, delete",
        passive_deletes=True,
    )
    department_id = Column(
        Integer, ForeignKey("department.id", ondelete="SET NULL"), nullable=True
    )
    department = relationship(
        "Department", back_populates="dcim_device", overlaps="=dcim_device"
    )
    circuit_termination = relationship(
        "CircuitTermination", back_populates="dcim_device", passive_deletes=True
    )


class Interface(Base, TimestampMixin):
    __tablename__ = "dcim_interface"
    __table_args__ = (UniqueConstraint("device_id", "name"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    if_index = Column(Integer, nullable=True)
    speed = Column(Integer, nullable=True)
    mode = Column(
        ENUM(
            "access",
            "hybrid",
            "trunk",
            "layer-3",
            name="interface_mode",
            create_type=False,
        )
    )
    interface_type = Column(String, nullable=False)
    mtu = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, server_default=expression.true())
    device_id = Column(Integer, ForeignKey("dcim_device.id", ondelete="CASCADE"))
    dcim_device = relationship(
        "Device", back_populates="dcim_interface", overlaps="dcim_interface"
    )
    circuit_termination = relationship(
        "CircuitTermination", back_populates="dcim_interface", passive_deletes=True
    )
    lag_interface_id = Column(
        Integer,
        ForeignKey("dcim_interface.id"),
        nullable=True,
        comment="port channel or eth-trunk",
    )
    lag_children = relationship(
        "Interface", foreign_keys=[lag_interface_id], lazy="selectin", join_depth=1
    )
    parent_interface_id = Column(
        Integer,
        ForeignKey("dcim_interface.id"),
        nullable=True,
        comment="child interface, like g0/0/1.0",
    )
    interface_children = relationship(
        "Interface", foreign_keys=[parent_interface_id], lazy="selectin", join_depth=1
    )
    vrf_id = Column(
        Integer, ForeignKey("ipam_vrf.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vrf = relationship(
        "VRF",
        back_populates="dcim_interface",
        overlaps="dcim_interface",
    )
    vlan_id = Column(
        Integer, ForeignKey("ipam_vlan.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vlan = relationship(
        "VLAN",
        back_populates="dcim_interface",
        overlaps="dcim_interface",
    )
    ipam_ip_address = relationship(
        "IPAddress", back_populates="dcim_interface", overlaps="dcim_interface"
    )
