from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import CIDR, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, PrimaryKeyMixin, TimestampMixin

__all__ = ("ASN", "Block", "IPAddress", "IPRange", "RIR", "IPRole")

# class GetAvailablePrefixesMixin:


#     def get_available_prefixes(self):
#         """get available prefixes within thie block or prefix as an IPSet"""
#         params = {
#             'prefix__net_contained': str(self.prefix)
#         }
#         if hasattr(self, 'var'):
#             params['vrf'] = self.vrf
#         stmt = select(Prefix).where(Prefix)


class RIR(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "ipam_rirs"
    is_private = Column(Boolean, server_default=expression.false())
    ipam_blocks = relationship(
        "Block", back_populates="ipam_rirs", passive_deletes=True
    )


class Block(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ipam_blocks"
    prefix = Column(CIDR, nullable=False)
    rir_id = Column(
        Integer, ForeignKey("ipam_rirs.id", ondelete="SET NULL"), nullable=True
    )
    ipam_rirs = relationship(
        "RIR", back_populates="ipam_blocks", overlaps="ipam_blocks"
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"))
    tenants = relationship(
        "Tenant", back_populates="ipam_blocks", overlaps="ipam_blocks"
    )
    description = Column(String, nullable=True)


class IPRole(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "ipam_roles"
    ipam_prefixes = relationship(
        "Prefix", back_populates="ipam_roles", passive_deletes=True
    )
    ipam_vlans = relationship("VLAN", back_populates="ipam_roles", passive_deletes=True)
    ipam_ip_ranges = relationship(
        "IPRange", back_populates="ipam_roles", passive_deletes=True
    )


class Prefix(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ipam_prefixes"
    prefix = Column(CIDR, nullable=False)
    status = Column(String, nullable=False)
    site_id = Column(
        Integer, ForeignKey("dcim_sites.id", ondelete="SET NULL"), nullable=True
    )
    dcim_sites = relationship(
        "Site", back_populates="ipam_prefixes", overlaps="ipam_prefixes"
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"))
    tenants = relationship(
        "Tenant", back_populates="ipam_prefixes", overlaps="ipam_prefixes"
    )
    role_id = Column(
        Integer, ForeignKey("ipam_roles.id", ondelete="SET NULL"), nullable=True
    )
    ipam_roles = relationship(
        "IPRole", back_populates="ipam_prefixes", overlaps="ipam_prefixes"
    )
    is_pool = Column(Boolean, server_default=expression.false())


class ASN(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ipam_asns"
    asn = Column(Integer, unique=True, nullable=False)
    description = Column(String, nullable=True)
    tenants = relationship(
        "Tenant",
        secondary="tenant_asn_link",
        overlaps="ipam_asns",
        back_populates="ipam_asns",
    )
    dcim_sites = relationship(
        "Site",
        secondary="dcim_site_asn_link",
        overlaps="ipam_asns",
        back_populates="ipam_asns",
    )


class IPRange(Base, PrimaryKeyMixin):
    __tablename__ = "ipam_ip_ranges"
    start_address = Column(INET)
    end_address = Column(INET)
    # TODO: add pydantic size unchangeable
    status = Column(String, nullable=False)
    size = Column(
        Integer,
    )
    vrf_id = Column(
        Integer, ForeignKey("ipam_vrfs.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vrfs = relationship(
        "VRF", back_populates="ipam_ip_ranges", overlaps="ipam_ip_ranges"
    )
    role_id = Column(
        Integer, ForeignKey("ipam_roles.id", ondelete="SET NULL"), nullable=True
    )
    ipam_roles = relationship(
        "IPRole", back_populates="ipam_ip_ranges", overlaps="ipam_ip_ranges"
    )
    description = Column(String, nullable=True)


class IPAddress(Base, PrimaryKeyMixin):
    __tablename__ = "ipam_ip_addresses"
    address = Column(INET, nullable=False)
    vrf_id = Column(
        Integer, ForeignKey("ipam_vrfs.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vrfs = relationship(
        "VRF", back_populates="ipam_ip_addresses", overlaps="ipam_ip_addresses"
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"))
    tenants = relationship(
        "Tenant", back_populates="ipam_ip_addresses", overlaps="ipam_ip_addresses"
    )
    status = Column(String, nullable=False)
    # add role Enum
    role = Column(String)
    dns_name = Column(String)
    description = Column(String, nullable=True)


class VLAN(Base, PrimaryKeyMixin):
    __tablename__ = "ipam_vlans"
    __table_args__ = (UniqueConstraint("site_id", "vlan_group_id", "vid", "id"),)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    site_id = Column(
        Integer, ForeignKey("dcim_sites.id", ondelete="SET NULL"), nullable=True
    )
    dcim_sites = relationship(
        "Site", back_populates="ipam_vlans", overlaps="ipam_vlans"
    )
    vlan_group_id = Column(
        Integer, ForeignKey("ipam_vlan_groups.id", ondelete="SET NULL"), nullable=True
    )
    ipam_vlan_groups = relationship(
        "VLANGroup", back_populates="ipam_vlans", overlaps="ipam_vlans"
    )
    vid = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    tenants = relationship("Tenant", back_populates="ipam_vlans", overlaps="ipam_vlans")
    role_id = Column(
        Integer, ForeignKey("ipam_roles.id", ondelete="SET NULL"), nullable=True
    )
    ipam_roles = relationship(
        "IPRole", back_populates="ipam_vlans", overlaps="ipam_vlans"
    )


class VLANGroup(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "ipam_vlan_groups"
    ipam_vlans = relationship(
        "VLAN", back_populates="ipam_vlan_groups", passive_deletes=True
    )


class VRFRouteTargetLink(Base, PrimaryKeyMixin):
    __tablename__ = "vrf_route_target_link"
    vrf_id = Column(Integer, ForeignKey("ipam_vrfs.id"), primary_key=True)
    route_target_id = Column(
        Integer, ForeignKey("ipam_route_targets.id"), primary_key=True
    )
    target_type = Column(String, nullable=False)


class VRF(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "ipam_vrfs"
    rd = Column(String, unique=True, nullable=True)
    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    tenants = relationship("Tenant", back_populates="ipam_vrfs", overlaps="ipam_vrfs")
    enforce_unique = Column(
        Boolean,
        server_default=expression.true(),
        comment="Enforce unique space, prevent duplicate IP/prefix",
    )
    description = Column(String, nullable=True)
    ipam_route_targets = relationship(
        "RouteTarget",
        secondary="vrf_route_target_link",
        overlaps="ipam_vrfs",
        back_populates="ipam_vrfs",
    )
    ipam_ip_ranges = relationship(
        "IPRange", back_populates="ipam_vrfs", passive_deletes=True
    )
    ipam_ip_addresses = relationship(
        "IPAddress", back_populates="ipam_vrfs", passive_deletes=True
    )


class RouteTarget(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "ipam_route_targets"
    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    tenants = relationship(
        "Tenant", back_populates="ipam_route_targets", overlaps="ipam_route_targets"
    )
    ipam_vrfs = relationship(
        "VRF",
        secondary="vrf_route_target_link",
        overlaps="ipam_route_targets",
        back_populates="ipam_route_targets",
    )
