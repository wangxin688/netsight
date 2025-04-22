from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from netsight.core.database import Base
from netsight.core.database.mixins import AuditLogMixin, AuditUserMixin
from netsight.core.database.types import PgCIDR, PgIpInterface, bool_false, bool_true, int_pk
from netsight.features._types import IPvAnyInterface, IPvAnyNetwork
from netsight.features.consts import IPAddressStatus, IPRangeStatus, PrefixStatus, VLANStatus

if TYPE_CHECKING:
    from netsight.features.admin.models import User
    from netsight.features.circuit.models import ISP
    from netsight.features.dcim.models import Interface
    from netsight.features.intend.models import IPRole
    from netsight.features.org.models import Site

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


class Block(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "block"
    __visible_name__ = {"en": "IP Block", "zh": "IP地址段"}
    __search_fields__ = {"block"}
    id: Mapped[int_pk]
    name: Mapped[str]
    block: Mapped[str] = mapped_column(PgCIDR, unique=True)
    size: Mapped[int]
    range: Mapped[str]
    is_private: Mapped[bool]
    description: Mapped[str | None]


class Prefix(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "prefix"
    __visible_name__ = {"en": "IP Prefix", "zh": "IP子网段"}
    __search_fields__ = {"prefix"}
    id: Mapped[int_pk]
    prefix: Mapped[IPvAnyNetwork] = mapped_column(PgCIDR, unique=True, index=True)
    status: Mapped[PrefixStatus] = mapped_column(ChoiceType(PrefixStatus, impl=String()))
    is_dhcp_pool: Mapped[bool_true]
    is_full: Mapped[bool_false]
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlan.id", ondelete="SET NULL"))
    vlan: Mapped["VLAN"] = relationship(backref="prefix")
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="SET NULL"))
    site: Mapped["Site"] = relationship(backref="prefix")
    role_id: Mapped[int | None] = mapped_column(ForeignKey("ip_role.id", ondelete="CASCADE"))
    role: Mapped["IPRole"] = relationship(back_populates="prefix", passive_deletes=True)
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship(backref="prefix")


class ASN(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "asn"
    __visible_name__ = {"en": "AS Number", "zh": "AS号"}
    __search_fields__ = {"asn"}
    id: Mapped[int_pk]
    asn: Mapped[int] = mapped_column(unique=True)
    description: Mapped[str | None]
    site: Mapped[list["Site"]] = relationship(secondary="site_asn", back_populates="asn")
    isp: Mapped[list["ISP"]] = relationship(secondary="isp_asn", back_populates="asn")


class IPRange(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "ip_range"
    __visible_name__ = {"en": "IP Range", "zh": "IP地址串"}
    id: Mapped[int_pk]
    start_address: Mapped[IPvAnyInterface] = mapped_column(PgIpInterface)
    end_address: Mapped[IPvAnyInterface] = mapped_column(PgIpInterface)
    status: Mapped[IPRangeStatus] = mapped_column(ChoiceType(IPRangeStatus, impl=String()))
    description: Mapped[str | None]
    vrf_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship(backref="ip_range")

    @property
    def size(self) -> int:
        return int(self.end_address) - int(self.start_address)


class IPAddress(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "ip_address"
    __visible_name__ = {"en": "IP Address", "zh": "IP地址"}
    __search_fields__ = {"address"}
    id: Mapped[int_pk]
    address: Mapped[IPvAnyInterface] = mapped_column(PgIpInterface)
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrf.id", ondelete="SET NULL"))
    vrf: Mapped["VRF"] = relationship(backref="ip_address")
    version: Mapped[int]
    status: Mapped[IPAddressStatus] = mapped_column(ChoiceType(IPAddressStatus, impl=String()))
    dns_name: Mapped[str | None]
    description: Mapped[str | None]
    owner: Mapped[list["User"]] = relationship(secondary="ip_address_user", backref="ip_address")
    interface_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface: Mapped["Interface"] = relationship(back_populates="ip_address")


class VLAN(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "vlan"
    __table_args__ = (UniqueConstraint("site_id", "vid"),)
    __search_fields__ = {"name", "vid"}
    id: Mapped[int_pk]
    name: Mapped[str]
    vid: Mapped[int]
    description: Mapped[str | None]
    status: Mapped[VLANStatus] = mapped_column(ChoiceType(VLANStatus, impl=String()))
    ip_address: Mapped[str]
    associated_interfaces: Mapped[list[str]] = mapped_column(ARRAY(String, dimensions=1), nullable=True)
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


class VRF(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "vrf"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    rd: Mapped[str] = mapped_column(unique=True)
    enforce_unique: Mapped[bool_true] = mapped_column(
        comment="Enforce unique space, prevent duplicate IP/prefix",
    )
    route_target: Mapped[list["RouteTarget"]] = relationship(secondary="vrf_route_target", back_populates="vrf")


class RouteTarget(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "route_target"
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    vrf: Mapped[list["VRF"]] = relationship(secondary="vrf_route_target", back_populates="route_target")
