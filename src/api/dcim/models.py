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
from sqlalchemy.dialects.postgresql import ENUM, INET, JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, TimestampMixin

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
    "Cable",
    "CablePath",
    "CableTermination",
)


class Region(Base, NameMixin):
    __tablename__ = "dcim_region"
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


class Site(Base, NameMixin, TimestampMixin):
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
        )
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


class Location(Base, NameMixin, TimestampMixin):
    """a sub location of site, like building, floor, idf, mdf and etc"""

    __tablename__ = "dcim_location"
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
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

    def __init__(self, name, status, site_id, parent_id=None, description=None):
        self.name = name
        self.site_id = site_id
        self.parent = parent_id
        self.description = description
        self.status = status


class RackRole(Base, NameMixin):
    __tablename__ = "dcim_rack_role"
    id = Column(Integer, primary_key=True)


class Rack(Base, NameMixin, TimestampMixin):
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
    status = Column(String, nullable=False)
    serial_num = Column(String, nullable=True)
    asset_tag = Column(String, nullable=True, unique=True)
    rack_type = Column(String, nullable=True)
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


class Manufacturer(Base, NameMixin):
    __tablename__ = "dcim_manufacturer"
    id = Column(Integer, primary_key=True)
    dcim_device_type = relationship(
        "DeviceType",
        back_populates="dcim_manufacturer",
        cascade="all, delete",
        passive_deletes=True,
    )


class DeviceType(Base):
    __tablename__ = "dcim_device_type"
    __table_args__ = (UniqueConstraint("manufacturer_id", "model"),)
    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(
        Integer, ForeignKey("dcim_manufacturer.id", ondelete="CASCADE")
    )
    dcim_manufacturer = relationship(
        "Manufacturer", back_populates="dcim_device_type", overlaps="dcim_device_type"
    )
    model = Column(String, nullable=False)
    u_height = Column(Float, server_default="1.0")
    is_full_depth = Column(Boolean, server_default=expression.true())
    dcim_device = relationship(
        "Device", back_populates="dcim_device_type", passive_deletes=True
    )


class DeviceRole(Base, NameMixin):
    id = Column(Integer, primary_key=True)
    __tablename__ = "dcim_device_role"
    vm_role = Column(Boolean, server_default=expression.false())
    dcim_device = relationship(
        "Device", back_populates="dcim_device_role", passive_deletes=True
    )
    server = relationship(
        "Server", back_populates="dcim_device_role", passive_deletes=True
    )


class Platform(Base, NameMixin):
    __tablename__ = "dcim_platform"
    id = Column(Integer, primary_key=True)
    napalm_driver = Column(String, nullable=True)
    napalm_args = Column(JSONB, nullable=True)
    dcim_device = relationship(
        "Device", back_populates="dcim_platform", passive_deletes=True
    )
    server = relationship(
        "Server", back_populates="dcim_platform", passive_deletes=True
    )


class Device(Base, TimestampMixin):
    __tablename__ = "dcim_device"
    __table_args__ = (
        UniqueConstraint("rack_id", "position"),
        UniqueConstraint("cluster_id", "name"),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    primary_ipv4 = Column(INET, nullable=False, index=True)
    primary_ipv6 = Column(INET, nullable=True)
    comments = Column(String, nullable=True)
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


class Interface(Base, TimestampMixin):
    __tablename__ = "dcim_interface"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    if_index = Column(Integer, nullable=True)
    speed = Column(Integer, nullable=True)
    mode = Column(
        ENUM("access", "trunk", "layer-3", name="mode_enum", create_type=False)
    )
    mtu = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, server_default=expression.true())
    device_id = Column(Integer, ForeignKey("dcim_device.id"))
    dcim_device = relationship(
        "Device", back_populates="dcim_interface", overlaps="dcim_interface"
    )
    # TODO: add support for vrf, vlan, ip address linking


class Cable(Base, NameMixin, TimestampMixin):
    __tablename__ = "dcim_cable"
    id = Column(Integer, primary_key=True)
    cable_type = Column(String, nullable=True)
    status = Column(String, nullable=False)
    dcim_cable_termination = relationship(
        "CableTermination", back_populates="dcim_cable", passive_deletes=True
    )


class CablePath:
    pass


class CableTermination(Base):
    __tablename__ = "dcim_cable_termination"
    id = Column(Integer, primary_key=True)
    cable_id = Column(Integer, ForeignKey("dcim_cable.id", ondelete="CASCADE"))
    dcim_cable = relationship(
        "Cable",
        back_populates="dcim_cable_termination",
        overlaps="dcim_cable_termination",
    )
