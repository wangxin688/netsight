from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import CIDR, ENUM, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, TimestampMixin

__all__ = (
    "SiteASN",
    "RIR",
    "Block",
    "IPRole",
    "Prefix",
    "ASN",
    "IPRange",
    "IPAddress",
    "VLAN",
    "VLANGroup",
    "VRFRouteTargetLink",
    "VRF",
    "RouteTarget",
)


class SiteASN(Base):
    __tablename__ = "dcim_site_asn_link"
    site_id = Column(Integer, ForeignKey("dcim_site.id"), primary_key=True)
    asn_id = Column(Integer, ForeignKey("ipam_asn.id"), primary_key=True)


class RIR(Base, NameMixin, TimestampMixin):
    __tablename__ = "ipam_rir"
    id = Column(Integer, primary_key=True)
    is_private = Column(Boolean, server_default=expression.false())
    ipam_block = relationship("Block", back_populates="ipam_rir", passive_deletes=True)


class Block(Base, TimestampMixin):
    __tablename__ = "ipam_block"
    id = Column(Integer, primary_key=True)
    prefix = Column(CIDR, nullable=False)
    rir_id = Column(
        Integer, ForeignKey("ipam_rir.id", ondelete="SET NULL"), nullable=True
    )
    ipam_rir = relationship("RIR", back_populates="ipam_block", overlaps="ipam_block")
    tenant_id = Column(
        Integer, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=True
    )
    tenant = relationship("Tenant", back_populates="ipam_block", overlaps="ipam_block")
    description = Column(String, nullable=True)


class IPRole(Base, NameMixin):
    __tablename__ = "ipam_role"
    id = Column(Integer, primary_key=True)
    ipam_prefix = relationship(
        "Prefix", back_populates="ipam_role", passive_deletes=True
    )
    ipam_vlan = relationship("VLAN", back_populates="ipam_role", passive_deletes=True)
    ipam_ip_range = relationship(
        "IPRange", back_populates="ipam_role", passive_deletes=True
    )


class Prefix(Base, TimestampMixin):
    __tablename__ = "ipam_prefix"
    id = Column(Integer, primary_key=True)
    prefix = Column(CIDR, nullable=False)
    status = Column(
        ENUM("Active", "Reserved", "Deprecated", name="vlan_status", create_type=False),
        nullable=False,
    )
    site_id = Column(
        Integer, ForeignKey("dcim_site.id", ondelete="SET NULL"), nullable=True
    )
    dcim_site = relationship(
        "Site", back_populates="ipam_prefix", overlaps="ipam_prefix"
    )
    tenant_id = Column(Integer, ForeignKey("tenant.id", ondelete="SET NULL"))
    tenant = relationship(
        "Tenant", back_populates="ipam_prefix", overlaps="ipam_prefix"
    )
    role_id = Column(
        Integer, ForeignKey("ipam_role.id", ondelete="SET NULL"), nullable=True
    )
    ipam_role = relationship(
        "IPRole", back_populates="ipam_prefix", overlaps="ipam_prefix"
    )
    is_pool = Column(Boolean, server_default=expression.false())


class ASN(Base, TimestampMixin):
    __tablename__ = "ipam_asn"
    id = Column(Integer, primary_key=True)
    asn = Column(Integer, unique=True, nullable=False)
    description = Column(String, nullable=True)
    tenant = relationship(
        "Tenant",
        secondary="tenant_ipam_asn_link",
        overlaps="ipam_asn",
        back_populates="ipam_asn",
    )
    dcim_site = relationship(
        "Site",
        secondary="dcim_site_asn_link",
        overlaps="ipam_asn",
        back_populates="ipam_asn",
    )


class IPRange(Base):
    __tablename__ = "ipam_ip_range"
    id = Column(Integer, primary_key=True)
    start_address = Column(INET)
    end_address = Column(INET)
    # TODO: add pydantic size unchangeable
    status = Column(
        ENUM("Active", "Reserved", "Deprecated", name="vlan_status", create_type=False),
        nullable=False,
    )
    size = Column(
        Integer,
    )
    vrf_id = Column(
        Integer, ForeignKey("ipam_vrf.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vrf = relationship(
        "VRF", back_populates="ipam_ip_range", overlaps="ipam_ip_range"
    )
    role_id = Column(
        Integer, ForeignKey("ipam_role.id", ondelete="SET NULL"), nullable=True
    )
    ipam_role = relationship(
        "IPRole", back_populates="ipam_ip_range", overlaps="ipam_ip_range"
    )
    description = Column(String, nullable=True)


class IPAddress(Base):
    __tablename__ = "ipam_ip_address"
    id = Column(Integer, primary_key=True)
    address = Column(INET, nullable=False, index=True)
    vrf_id = Column(
        Integer, ForeignKey("ipam_vrf.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vrf = relationship(
        "VRF", back_populates="ipam_ip_address", overlaps="ipam_ip_address"
    )
    tenant_id = Column(Integer, ForeignKey("tenant.id", ondelete="SET NULL"))
    tenant = relationship(
        "Tenant", back_populates="ipam_ip_address", overlaps="ipam_ip_address"
    )
    status = Column(
        ENUM(
            "Active",
            "Reserved",
            "Deprecated",
            "DHCP",
            "Available",
            name="ip_status",
            create_type=False,
        ),
        nullable=False,
    )
    dns_name = Column(String)
    description = Column(String, nullable=True)


class VLAN(Base):
    __tablename__ = "ipam_vlan"
    __table_args__ = (UniqueConstraint("site_id", "vlan_group_id", "vid", "id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(
        ENUM("Active", "Reserved", "Deprecated", name="vlan_status", create_type=False),
        nullable=False,
    )
    site_id = Column(
        Integer, ForeignKey("dcim_site.id", ondelete="SET NULL"), nullable=True
    )
    dcim_site = relationship("Site", back_populates="ipam_vlan", overlaps="ipam_vlan")
    vlan_group_id = Column(
        Integer, ForeignKey("ipam_vlan_group.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vlan_group = relationship(
        "VLANGroup", back_populates="ipam_vlan", overlaps="ipam_vlan"
    )
    vid = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    tenant_id = Column(
        Integer, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=True
    )
    tenant = relationship("Tenant", back_populates="ipam_vlan", overlaps="ipam_vlan")
    role_id = Column(
        Integer, ForeignKey("ipam_role.id", ondelete="SET NULL"), nullable=True
    )
    ipam_role = relationship("IPRole", back_populates="ipam_vlan", overlaps="ipam_vlan")


class VLANGroup(Base, NameMixin):
    __tablename__ = "ipam_vlan_group"
    id = Column(Integer, primary_key=True)
    ipam_vlan = relationship(
        "VLAN", back_populates="ipam_vlan_group", passive_deletes=True
    )


class VRFRouteTargetLink(Base):
    __tablename__ = "ipam_vrf_route_target_link"
    id = Column(Integer, primary_key=True)
    vrf_id = Column(Integer, ForeignKey("ipam_vrf.id"), primary_key=True)
    route_target_id = Column(
        Integer, ForeignKey("ipam_route_target.id"), primary_key=True
    )
    target_type = Column(String, nullable=False)


class VRF(Base, NameMixin):
    __tablename__ = "ipam_vrf"
    id = Column(Integer, primary_key=True)
    rd = Column(String, unique=True, nullable=True)
    tenant_id = Column(
        Integer, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=True
    )
    tenant = relationship("Tenant", back_populates="ipam_vrf", overlaps="ipam_vrf")
    enforce_unique = Column(
        Boolean,
        server_default=expression.true(),
        comment="Enforce unique space, prevent duplicate IP/prefix",
    )
    description = Column(String, nullable=True)
    ipam_route_target = relationship(
        "RouteTarget",
        secondary="ipam_vrf_route_target_link",
        overlaps="ipam_vrf",
        back_populates="ipam_vrf",
    )
    ipam_ip_range = relationship(
        "IPRange", back_populates="ipam_vrf", passive_deletes=True
    )
    ipam_ip_address = relationship(
        "IPAddress", back_populates="ipam_vrf", passive_deletes=True
    )


class RouteTarget(Base, NameMixin):
    __tablename__ = "ipam_route_target"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(
        Integer, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=True
    )
    tenant = relationship(
        "Tenant", back_populates="ipam_route_target", overlaps="ipam_route_target"
    )
    ipam_vrf = relationship(
        "VRF",
        secondary="ipam_vrf_route_target_link",
        overlaps="ipam_route_target",
        back_populates="ipam_route_target",
    )
