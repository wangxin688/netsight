from typing import List, Literal

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import CIDR, ENUM, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from src.app.dcim import models as dcim_models
from src.db.db_base import Base
from src.db.db_mixin import AuditLogMixin, NameMixin, TimestampMixin

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
    "VRFRouteTarget",
    "VRF",
    "RouteTarget",
)


class SiteASN(Base):
    __tablename__ = "dcim_site_asn_link"
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("dcim_site.id"), primary_key=True)
    asn_id: Mapped[int] = mapped_column(Integer, ForeignKey("ipam_asn.id"), primary_key=True)


class RIR(Base, TimestampMixin):
    __tablename__ = "ipam_rir"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())
    ipam_block: Mapped[List["Block"]] = relationship("Block", back_populates="ipam_rir", passive_deletes=True)


class Block(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "ipam_block"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    block: Mapped[CIDR] = mapped_column(CIDR, nullable=False)
    rir_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ipam_rir.id", ondelete="SET NULL"), nullable=True)
    ipam_rir: Mapped["RIR"] = relationship("RIR", back_populates="ipam_block", overlaps="ipam_block")
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class IPRole(Base, TimestampMixin):
    __tablename__ = "ipam_role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    ipam_prefix: Mapped[List["Prefix"]] = relationship("Prefix", back_populates="ipam_role", passive_deletes=True)
    ipam_vlan: Mapped[List["VLAN"]] = relationship("VLAN", back_populates="ipam_role", passive_deletes=True)
    ipam_ip_range: Mapped[List["IPRange"]] = relationship("IPRange", back_populates="ipam_role", passive_deletes=True)


class Prefix(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "ipam_prefix"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prefix: Mapped[CIDR] = mapped_column(CIDR, nullable=False)
    status: Mapped[Literal["Active", "Reserved", "Deprecated"]] = mapped_column(
        ENUM("Active", "Reserved", "Deprecated", name="vlan_status"), nullable=False
    )
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("dcim_site.id", ondelete="SET NULL"), nullable=True)
    dcim_site: Mapped["dcim_models.Site"] = relationship("Site", back_populates="ipam_prefix", overlaps="ipam_prefix")
    role_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ipam_role.id", ondelete="SET NULL"), nullable=True)
    ipam_role: Mapped["IPRole"] = relationship("IPRole", back_populates="ipam_prefix", overlaps="ipam_prefix")
    is_pool: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())
    is_full: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())


class ASN(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "ipam_asn"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asn: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    description: Mapped[int] = mapped_column(String, nullable=True)
    dcim_site: Mapped[List["dcim_models.Site"]] = relationship(
        "Site", secondary="dcim_site_asn_link", overlaps="ipam_asn", back_populates="ipam_asn"
    )


class IPRange(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "ipam_ip_range"
    id = mapped_column(Integer, primary_key=True)
    start_address: Mapped[INET] = mapped_column(INET)
    end_address: Mapped[INET] = mapped_column(INET)
    # TODO: add pydantic size unchangeable
    status: Literal["Active", "Reserved", "Deprecated"] = mapped_column(
        ENUM("Active", "Reserved", "Deprecated", name="vlan_status"),
        nullable=False,
    )
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    vrf_id: Mapped[int] = mapped_column(Integer, ForeignKey("ipam_vrf.id", ondelete="SET NULL"), nullable=True)
    ipam_vrf: Mapped["VRF"] = relationship("VRF", back_populates="ipam_ip_range", overlaps="ipam_ip_range")
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("ipam_role.id", ondelete="SET NULL"), nullable=True)
    ipam_role: Mapped["IPRole"] = relationship("IPRole", back_populates="ipam_ip_range", overlaps="ipam_ip_range")
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class IPAddress(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "ipam_ip_address"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    address:Mapped[INET] = mapped_column(INET, nullable=False, index=True)
    vrf_id:Mapped[int] = mapped_column(Integer, ForeignKey("ipam_vrf.id", ondelete="SET NULL"), nullable=True)
    ipam_vrf:Mapped["VRF"] = relationship("VRF", back_populates="ipam_ip_address", overlaps="ipam_ip_address")
    version:Mapped[Literal["IPv4", "IPv6"]] = mapped_column(ENUM("IPv4", "IPv6", name="ip_version", create_type=False), nullable=False)
    status: Mapped[Literal["Active",
            "Reserved",
            "Deprecated",
            "DHCP",
            "Available"]] = mapped_column(
        ENUM(
            "Active",
            "Reserved",
            "Deprecated",
            "DHCP",
            "Available",
            name="ip_status"
        ),nullable=False,
    )
    dns_name: Mapped[str|None] = mapped_column(String, nullable=True)
    description:Mapped[str|None] = mapped_column(String, nullable=True)
    owners:Mapped[str|None] = mapped_column(String, nullable=True)
    interface_id: Mapped[int|None] = mapped_column(Integer, ForeignKey("dcim_interface.id", ondelete="SET NULL"), nullable=True)
    dcim_interface:Mapped["dcim_models.Interface"] = relationship("Interface", back_populates="ipam_ip_address", overlaps="ipam_ip_address")


class VLAN(Base, TimestampMixin, AuditLogMixin):
    __tablename__ = "ipam_vlan"
    __table_args__ = (UniqueConstraint("site_id", "vlan_group_id", "vid", "id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=True)
    status = mapped_column(
        ENUM("Active", "Reserved", "Deprecated", name="vlan_status", create_type=False), nullable=False
    )
    site_id = mapped_column(Integer, ForeignKey("dcim_site.id", ondelete="SET NULL"), nullable=True)
    dcim_site = relationship("Site", back_populates="ipam_vlan", overlaps="ipam_vlan")
    vlan_group_id = mapped_column(Integer, ForeignKey("ipam_vlan_group.id", ondelete="SET NULL"), nullable=True)
    ipam_vlan_group = relationship("VLANGroup", back_populates="ipam_vlan", overlaps="ipam_vlan")
    vid = mapped_column(Integer, nullable=False)
    role_id = mapped_column(Integer, ForeignKey("ipam_role.id", ondelete="SET NULL"), nullable=True)
    ipam_role = relationship("IPRole", back_populates="ipam_vlan", overlaps="ipam_vlan")
    dcim_interface = relationship("Interface", back_populates="ipam_vlan", passive_deletes=True)


class VLANGroup(Base, NameMixin, AuditLogMixin):
    __tablename__ = "ipam_vlan_group"
    id = mapped_column(Integer, primary_key=True)
    ipam_vlan = relationship("VLAN", back_populates="ipam_vlan_group", passive_deletes=True)


class VRFRouteTarget(Base):
    __tablename__ = "ipam_vrf_route_target_link"
    id = mapped_column(Integer, primary_key=True)
    vrf_id = mapped_column(Integer, ForeignKey("ipam_vrf.id"), primary_key=True)
    route_target_id = mapped_column(Integer, ForeignKey("ipam_route_target.id"), primary_key=True)
    target = mapped_column(String, nullable=False)


class VRF(Base, NameMixin, AuditLogMixin):
    __tablename__ = "ipam_vrf"
    id = mapped_column(Integer, primary_key=True)
    rd = mapped_column(String, unique=True, nullable=True)
    enforce_unique = mapped_column(
        Boolean,
        server_default=expression.true(),
        comment="Enforce unique space, prevent duplicate IP/prefix",
    )
    ipam_route_target = relationship(
        "RouteTarget",
        secondary="ipam_vrf_route_target_link",
        overlaps="ipam_vrf",
        back_populates="ipam_vrf",
    )
    ipam_ip_range = relationship("IPRange", back_populates="ipam_vrf", passive_deletes=True)
    ipam_ip_address = relationship("IPAddress", back_populates="ipam_vrf", passive_deletes=True)
    dcim_interface = relationship("Interface", back_populates="ipam_vrf", passive_deletes=True)


class RouteTarget(Base, NameMixin, AuditLogMixin):
    __tablename__ = "ipam_route_target"
    id = mapped_column(Integer, primary_key=True)
    ipam_vrf = relationship(
        "VRF",
        secondary="ipam_vrf_route_target_link",
        overlaps="ipam_route_target",
        back_populates="ipam_route_target",
    )
