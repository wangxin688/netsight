from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import CIDR, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db._types import bool_false, bool_true, int_pk
from src.db.base import Base
from src.db.mixins import AuditLogMixin, AuditTimeMixin

if TYPE_CHECKING:
    from src.arch.models import IPRole
    from src.auth.models import User
    from src.circuit.models import ISP
    from src.dcim.models import Interface, Site


class SiteASN(Base):
    __tablename__ = "site_asn"
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), primary_key=True)
    asn_id: Mapped[int] = mapped_column(ForeignKey("asn.id"), primary_key=True)


class IPAddressUser(Base):
    __tablename__ = "ip_address_user"
    ip_address_id: Mapped[int] = mapped_column(ForeignKey("site.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("site.id"), primary_key=True)


class Block(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "block"
    __visible_name__ = {"en_US": "IP Block", "zh_CN": "IP地址段"}
    __search_fields__ = {"block"}
    id: Mapped[int_pk]
    block: Mapped[str] = mapped_column(CIDR, unique=True)
    description: Mapped[str | None]


class Prefix(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "prefix"
    __visible_name__ = {"en_US": "IP Prefix", "zh_CN": "IP子网段"}
    __search_fields__ = {"prefix"}
    id: Mapped[int_pk]
    prefix: Mapped[str] = mapped_column(CIDR, unique=True)
    status: Mapped[int]
    is_dhcp_pool: Mapped[bool_true]
    is_full: Mapped[bool_false]
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlan.id", ondelete="SET NULL"))
    vlan: Mapped["VLAN"] = relationship(back_populates="prefix")
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="SET NULL"))
    site: Mapped["Site"] = relationship("Site", back_populates="prefix", overlaps="prefix")
    role_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ip_role.id", ondelete="SET NULL"), nullable=True)
    ip_role: Mapped["IPRole"] = relationship(back_populates="prefix", overlaps="prefix")


class ASN(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "asn"
    __visible_name__ = {"en_US": "AS Number", "zh_CN": "AS号"}
    __search_fields__ = {"asn"}
    id: Mapped[int_pk]
    asn: Mapped[int] = mapped_column(unique=True)
    description: Mapped[str | None]
    site: Mapped[list["Site"]] = relationship(secondary="site_asn", back_populates="asn")
    isp: Mapped[list["ISP"]] = relationship(secondary="isp_asn", back_populates="asn")


class IPRange(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "ip_range"
    __visible_name__ = {"en_US": "IP Range", "zh_CN": "IP地址串"}
    id: Mapped[int_pk]
    start_address: Mapped[str] = mapped_column(INET)
    end_address: Mapped[str] = mapped_column(INET)
    status: Mapped[int]
    size: Mapped[int]
    description: Mapped[str | None]
    vrf_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship("VRF", back_populates="ip_range")
    role_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ip_role.id", ondelete="SET NULL"))
    ip_role: Mapped["IPRole"] = relationship(back_populates="ip_range")


class IPAddress(Base, AuditTimeMixin):
    __tablename__ = "ip_address"
    __visible_name__ = {"en_US": "IP Address", "zh_CN": "IP地址"}
    __search_fields__ = {"address"}
    id: Mapped[int_pk]
    address: Mapped[str] = mapped_column(INET)
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrf.id", ondelete="SET NULL"))
    ipam_vrf: Mapped["VRF"] = relationship(back_populates="ip_address")
    version: Mapped[int]
    status: Mapped[int]
    dns_name: Mapped[str | None]
    description: Mapped[str | None]
    owner: Mapped[list["User"]] = relationship(secondary="ip_address_user", back_populates="ip_address")
    interface_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface: Mapped["Interface"] = relationship(back_populates="ip_address")


class VLAN(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "ipam_vlan"
    __table_args__ = UniqueConstraint("site_id", "vid")
    __search_fields__ = {"name", "vid"}
    id: Mapped[int_pk]
    name: Mapped[str]
    vid: Mapped[int]
    description: Mapped[str | None]
    status: Mapped[int]
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="vlan", passive_deletes=True)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("ip_role.id", ondelete="SET NULL"))
    ip_role: Mapped["IPRole"] = relationship(back_populates="vlan")


class VRFRouteTarget(Base):
    __tablename__ = "vrf_route_target"
    id: Mapped[int_pk]
    vrf_id: Mapped[int] = mapped_column(ForeignKey("vrf.id"), primary_key=True)
    route_target_id: Mapped[int] = mapped_column(ForeignKey("route_target.id"), primary_key=True)
    target: Mapped[str]


class VRF(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "vrf"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    rd: Mapped[str] = mapped_column(unique=True)
    enforce_unique: Mapped[bool_true] = mapped_column(
        comment="Enforce unique space, prevent duplicate IP/prefix",
    )
    route_target: Mapped[list["RouteTarget"]] = relationship(secondary="vrf_route_target", back_populates="vrf")
    ip_range = relationship("IPRange", back_populates="ipam_vrf", passive_deletes=True)
    ip_address = relationship("IPAddress", back_populates="ipam_vrf", passive_deletes=True)
    interface = relationship("Interface", back_populates="ipam_vrf", passive_deletes=True)


class RouteTarget(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "route_target"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    vrf: Mapped[list["VRF"]] = relationship(secondary="vrf_route_target", back_populates="route_target")
