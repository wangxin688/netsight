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
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, PrimaryKeyMixin, TimestampMixin


class Region(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "dcim_regions"
    parent_id = Column(Integer, ForeignKey(id))
    dcim_sites = relationship(
        "Site",
        back_populates="dcim_regions",
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


class SiteGroup(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "dcim_site_groups"
    group_code = Column(String, unique=True, nullable=False)
    dcim_sites = relationship(
        "Site",
        back_populates="dcim_site_groups",
        passive_deletes=True,
    )


class Site(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "dcim_sites"
    site_code = Column(String, unique=True, nullable=False)
    status = Column(String)
    region_id = Column(
        Integer, ForeignKey("dcim_regions.id", ondelete="SET NULL"), nullable=True
    )
    dcim_regions = relationship(
        "Region", back_populates="dcim_sites", overlaps="dcim_sites"
    )
    group_id = Column(
        Integer, ForeignKey("dcim_site_groups.id", ondelete="SET NULL"), nullable=True
    )
    dcim_site_groups = relationship(
        "SiteGroup", back_populates="dcim_sites", overlaps="dcim_sites"
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
    tenants = relationship("Tenant", back_populates="dcim_sites", overlaps="dcim_sites")
    facility = Column(String, nullable=True)
    ipam_asns = relationship(
        "ASN",
        secondary="dcim_site_asn_link",
        overlaps="dcim_sites",
        back_populates="dcim_sites",
    )
    # TODO: pydantic timezone fields
    time_zone = Column(String, nullable=True)
    physical_address = Column(String, nullable=True)
    shipping_address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    contacts = relationship(
        "Contact",
        secondary="dcim_site_contact_link",
        overlaps="dcim_sites",
        back_populates="dcim_sites",
    )
    # vlan_groups =
    dcim_locations = relationship(
        "Location",
        back_populates="dcim_sites",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_racks = relationship(
        "Rack",
        back_populates="dcim_sites",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_devices = relationship(
        "Device",
        back_populates="dcim_sites",
        cascade="all, delete",
        passive_deletes=True,
    )
    # image = Column(LargeBinary, nullable=True) or a url in cdn or object storage
    ipam_prefixes = relationship(
        "Prefix", back_populates="dcim_sites", passive_deletes=True
    )
    ipam_vlans = relationship("VLAN", back_populates="dcim_sites", passive_deletes=True)


class Location(Base, PrimaryKeyMixin, NameMixin):
    """a sub location of site, like building, floor, idf, mdf and etc"""

    __tablename__ = "dcim_locations"
    status = Column(String, nullable=False)
    site_id = Column(Integer, ForeignKey("dcim_sites.id", ondelete="CASCADE"))
    dcim_sites = relationship(
        "Site", back_populates="dcim_locations", overlaps="dcim_locations"
    )
    dcim_racks = relationship(
        "Rack",
        back_populates="dcim_locations",
        cascade="all, delete",
        passive_deletes=True,
    )
    dcim_devices = relationship(
        "Device",
        back_populates="dcim_locations",
        passive_deletes=True,
    )
    parent_id = Column(Integer, ForeignKey(id))
    # tenant?
    # vlan_group?
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


class RackRole(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "dcim_rack_roles"


class Rack(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "dcim_racks"
    facility_id = Column(String, nullable=True)
    site_id = Column(Integer, ForeignKey("dcim_sites.id", ondelete="CASCADE"))
    dcim_sites = relationship(
        "Site", back_populates="dcim_racks", overlaps="dcim_racks"
    )
    location_id = Column(
        Integer, ForeignKey("dcim_locations.id", ondelete="SET NULL"), nullable=True
    )
    dcim_locations = relationship(
        "Location", back_populates="dcim_racks", overlaps="dcim_racks"
    )
    dcim_devices = relationship(
        "Device",
        back_populates="dcim_racks",
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


class Manufacturer(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "dcim_manufacturers"
    dcim_device_types = relationship(
        "DeviceType",
        back_populates="dcim_manufacturers",
        cascade="all, delete",
        passive_deletes=True,
    )


class DeviceType(Base, PrimaryKeyMixin):
    __tablename__ = "dcim_device_types"
    __table_args__ = (UniqueConstraint("manufacturer_id", "model"),)
    manufacturer_id = Column(
        Integer, ForeignKey("dcim_manufacturers.id", ondelete="CASCADE")
    )
    dcim_manufacturers = relationship(
        "Manufacturer", back_populates="dcim_device_types", overlaps="dcim_device_types"
    )
    model = Column(String, nullable=False)
    u_height = Column(Float, server_default="1.0")
    is_full_depth = Column(Boolean, server_default=expression.true())
    dcim_devices = relationship(
        "Device", back_populates="dcim_device_types", passive_deletes=True
    )


class ModuleType:
    pass


class Module:
    pass


class DeviceRole(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "dcim_device_roles"
    vm_role = Column(Boolean, server_default=expression.false())
    dcim_devices = relationship(
        "Device", back_populates="dcim_device_roles", passive_deletes=True
    )


class Platform(Base, NameMixin):
    __tablename__ = "dcim_platforms"
    napalm_driver = Column(String, nullable=True)
    napalm_args = Column(JSONB, nullable=True)
    dcim_devices = relationship(
        "Device", back_populates="dcim_platforms", passive_deletes=True
    )


class Device(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "dcim_devices"
    __table_args__ = (
        UniqueConstraint("rack_id", "position"),
        UniqueConstraint("chassis_id", "name"),
    )
    primary_ipv4 = Column(INET, nullable=True)
    primary_ipv6 = Column(INET, nullable=True)
    comments = Column(String, nullable=True)
    device_type_id = Column(
        Integer, ForeignKey("dcim_device_types.id", ondelete="SET NULL"), nullable=True
    )
    dcim_device_types = relationship(
        "DeviceType", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    device_role_id = Column(
        Integer, ForeignKey("dcim_device_roles.id", ondelete="SET NULL"), nullable=True
    )
    dcim_device_roles = relationship(
        "DeviceRole", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    platform_id = Column(
        Integer, ForeignKey("dcim_platforms.id", ondelete="SET NULL"), nullable=True
    )
    dcim_platforms = relationship(
        "Platform", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    site_id = Column(Integer, ForeignKey("dcim_sites.id", ondelete="CASCADE"))
    dcim_sites = relationship(
        "Site", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    location_id = Column(
        Integer, ForeignKey("dcim_locations.id", ondelete="SET NULL"), nullable=True
    )
    dcim_locations = relationship(
        "Location", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    rack_id = Column(
        Integer, ForeignKey("dcim_racks.id", ondelete="SET NULL"), nullable=True
    )
    dcim_racks = relationship(
        "Rack", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    position = Column(Float, nullable=True)
    serial_num = Column(String, nullable=True)
    asset_tag = Column(String, unique=True, nullable=True)
    status = Column(String, nullable=False)
    # TODO: virtualization
    # cluster_id = Column(Integer, ForeignKey("virtualization_clusters.id", ondelete="SET NULL"), nullable=True)
    # virtualization_clusters = relationship(
    #     "Cluster", back_populates="dcim_devices", overlaps="dcim_devices"
    # )
    chassis_id = Column(
        Integer,
        ForeignKey("dcim_virtual_chassis.id", ondelete="SET NULL"),
        nullable=True,
    )
    dcim_virtual_chassis = relationship(
        "VirtualChassis", back_populates="dcim_devices", overlaps="dcim_devices"
    )
    comments = Column(Text, nullable=True)


class VirtualChassis(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "dcim_virtual_chassis"
    domain = Column(String, nullable=True)
    dcim_devices = relationship(
        "Device",
        back_populates="dcim_virtual_chassis",
        passive_deletes=True,
    )


class Interface:
    pass


class Cable(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "dcim_cables"
    cable_type = Column(String, nullable=True)
    status = Column(String, nullable=False)
    dcim_cable_terminations = relationship(
        "CableTermination", back_populates="dcim_cables", passive_deletes=True
    )


class CablePath:
    pass


class CableTermination(Base, PrimaryKeyMixin):
    __tablename__ = "dcim_cable_terminations"
    id = Column(Integer, primary_key=True)
    cable_id = Column(Integer, ForeignKey("dcim_cables.id", ondelete="CASCADE"))
    dcim_cables = relationship(
        "Cable",
        back_populates="dcim_cable_terminations",
        overlaps="dcim_cable_terminations",
    )
