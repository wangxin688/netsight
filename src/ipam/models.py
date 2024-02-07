from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from src.consts import IPAddressStatus, IPRangeStatus, PrefixStatus, VLANStatus
from src.db.base import Base
from src.db.db_types import IPvAnyInterface, IPvAnyNetwork, PgCIDR, PgIpInterface, bool_false, bool_true, int_pk
from src.db.mixins import AuditLogMixin

if TYPE_CHECKING:
    from src.arch.models import IPRole
    from src.auth.models import User
    from src.circuit.models import ISP
    from src.dcim.models import Interface, Site

__all__ = (
    "IPAddress",
    "IPRange",
    "Prefix",
    "VRF",
    "RouteTarget",
    "SiteASN",
    "IPAddressUser",
    "Block",
    "ASN",
    "VLAN",
    "VRFRouteTarget",
)


class SiteASN(Base):
    __tablename__ = "site_asn"
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), primary_key=True)
    asn_id: Mapped[int] = mapped_column(ForeignKey("asn.id"), primary_key=True)


class IPAddressUser(Base):
    __tablename__ = "ip_address_user"
    ip_address_id: Mapped[int] = mapped_column(ForeignKey("ip_address.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class Block(Base, AuditLogMixin):
    __tablename__ = "block"
    __visible_name__ = {"en_US": "IP Block", "zh_CN": "IP地址段"}
    __search_fields__ = {"block"}
    # __org__ = True
    # __table_args__ = UniqueConstraint("pregix", "organization_id")
    id: Mapped[int_pk]
    name: Mapped[str]
    block: Mapped[IPvAnyNetwork] = mapped_column(PgCIDR, unique=True)
    is_private: Mapped[bool]
    description: Mapped[str | None]


class Prefix(Base, AuditLogMixin):
    __tablename__ = "prefix"
    __visible_name__ = {"en_US": "IP Prefix", "zh_CN": "IP子网段"}
    __search_fields__ = {"prefix"}
    # __org__ = True
    # __table_args__ = UniqueConstraint("prefix", "organization_id")
    id: Mapped[int_pk]
    prefix: Mapped[IPvAnyNetwork] = mapped_column(PgCIDR, unique=True, index=True)
    status: Mapped[PrefixStatus] = mapped_column(ChoiceType(PrefixStatus))
    is_dhcp_pool: Mapped[bool_true]
    is_full: Mapped[bool_false]
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlan.id", ondelete="SET NULL"))
    vlan: Mapped["VLAN"] = relationship(backref="prefix")
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="SET NULL"))
    site: Mapped["Site"] = relationship(backref="prefix")
    role_id: Mapped[int | None] = mapped_column(ForeignKey("ip_role.id", ondelete="SET NULL"))
    role: Mapped["IPRole"] = relationship(back_populates="prefix")
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship(backref=prefix)


class ASN(Base, AuditLogMixin):
    __tablename__ = "asn"
    __visible_name__ = {"en_US": "AS Number", "zh_CN": "AS号"}
    __search_fields__ = {"asn"}
    id: Mapped[int_pk]
    asn: Mapped[int] = mapped_column(unique=True)
    description: Mapped[str | None]
    site: Mapped[list["Site"]] = relationship(secondary="site_asn", back_populates="asn")
    isp: Mapped[list["ISP"]] = relationship(secondary="isp_asn", back_populates="asn")


class IPRange(Base, AuditLogMixin):
    __tablename__ = "ip_range"
    __visible_name__ = {"en_US": "IP Range", "zh_CN": "IP地址串"}
    id: Mapped[int_pk]
    start_address: Mapped[IPvAnyInterface] = mapped_column(PgIpInterface)
    end_address: Mapped[IPvAnyInterface] = mapped_column(PgIpInterface)
    status: Mapped[IPRangeStatus] = mapped_column(ChoiceType(IPRangeStatus))
    description: Mapped[str | None]
    vrf_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship("VRF", backref="ip_range")

    @property
    def size(self) -> int:
        return int(self.end_address) - int(self.start_address)


class IPAddress(Base, AuditLogMixin):
    __tablename__ = "ip_address"
    __visible_name__ = {"en_US": "IP Address", "zh_CN": "IP地址"}
    __search_fields__ = {"address"}
    id: Mapped[int_pk]
    address: Mapped[IPvAnyInterface] = mapped_column(PgIpInterface)
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship(backref="ip_address")
    version: Mapped[int]
    status: Mapped[IPAddressStatus] = mapped_column(ChoiceType(IPAddressStatus))
    dns_name: Mapped[str | None]
    description: Mapped[str | None]
    owner: Mapped[list["User"]] = relationship(secondary="ip_address_user", backref="ip_address")
    interface_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface: Mapped["Interface"] = relationship(back_populates="ip_address")


class VLAN(Base, AuditLogMixin):
    __tablename__ = "vlan"
    __table_args__ = (UniqueConstraint("site_id", "vid"),)
    __search_fields__ = {"name", "vid"}
    id: Mapped[int_pk]
    name: Mapped[str]
    vid: Mapped[int]
    description: Mapped[str | None]
    status: Mapped[VLANStatus] = mapped_column(ChoiceType(VLANStatus))
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="vlan", passive_deletes=True)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("ip_role.id", ondelete="SET NULL"))
    role: Mapped["IPRole"] = relationship(back_populates="vlan")


class VRFRouteTarget(Base):
    __tablename__ = "vrf_route_target"
    id: Mapped[int_pk]
    vrf_id: Mapped[int] = mapped_column(ForeignKey("vrf.id"), primary_key=True)
    route_target_id: Mapped[int] = mapped_column(ForeignKey("route_target.id"), primary_key=True)
    target: Mapped[str]


class VRF(Base, AuditLogMixin):
    __tablename__ = "vrf"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    rd: Mapped[str] = mapped_column(unique=True)
    enforce_unique: Mapped[bool_true] = mapped_column(
        comment="Enforce unique space, prevent duplicate IP/prefix",
    )
    route_target: Mapped[list["RouteTarget"]] = relationship(secondary="vrf_route_target", back_populates="vrf")


class RouteTarget(Base, AuditLogMixin):
    __tablename__ = "route_target"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    vrf: Mapped[list["VRF"]] = relationship(secondary="vrf_route_target", back_populates="route_target")
