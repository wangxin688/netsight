from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from netsight.core.database import Base
from netsight.core.database.mixins import AuditLogMixin, AuditUserMixin
from netsight.core.database.types import (
    PgIpAddress,
    PgIpInterface,
    date_optional,
    i18n_name,
    int_pk,
)
from netsight.features._types import IPvAnyAddress, IPvAnyInterface
from netsight.features.consts import CircuitStatus

if TYPE_CHECKING:
    from netsight.features.dcim.models import Device, Interface
    from netsight.features.intend.models import CircuitType
    from netsight.features.ipam.models import ASN
    from netsight.features.org.models import Site

__all__ = ("Circuit", "ISP", "ISPASN")


class Circuit(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "circuit"
    __visible_name__ = {"en": "Circuit", "zh": "线路"}
    __search_fields__ = {"name", "slug", "cid"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    cid: Mapped[str | None] = mapped_column(unique=True)
    status: Mapped[CircuitStatus] = mapped_column(ChoiceType(CircuitStatus, impl=String()))
    install_date: Mapped[date_optional]
    purchase_term: Mapped[str | None]
    bandwidth: Mapped[int] = mapped_column(comment="Mbps")
    comments: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer_available_ip: Mapped[list[IPvAnyInterface] | None] = mapped_column(ARRAY(PgIpInterface), nullable=True)
    manufacturer_available_gateway: Mapped[list[IPvAnyAddress] | None] = mapped_column(
        ARRAY(PgIpAddress), nullable=True
    )
    isp_id: Mapped[int] = mapped_column(ForeignKey("isp.id", ondelete="RESTRICT"))
    isp: Mapped["ISP"] = relationship(back_populates="circuit")
    circuit_type_id: Mapped[int] = mapped_column(ForeignKey("circuit_type.id", ondelete="RESTRICT"))
    circuit_type: Mapped["CircuitType"] = relationship(backref="circuit")
    site_a_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="RESTRICT"))
    site_a: Mapped["Site"] = relationship(foreign_keys=[site_a_id], backref="a_circuit")
    device_a_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="RESTRICT"))
    device_a: Mapped["Device"] = relationship(foreign_keys=[device_a_id], backref="a_circuit")
    interface_a_id: Mapped[int] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface_a: Mapped["Interface"] = relationship(foreign_keys=[interface_a_id], backref="a_circuit")
    site_z_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="RESTRICT"))
    site_z: Mapped["Site"] = relationship(foreign_keys=[site_z_id], backref="z_circuit")
    device_z_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="RESTRICT"))
    device_z: Mapped["Device"] = relationship(foreign_keys=[device_z_id], backref="z_circuit")
    interface_z_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface_z: Mapped["Interface"] = relationship(foreign_keys=[interface_z_id], backref="z_circuit")


class ISP(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "isp"
    __visible_name__ = {"en": "ISP", "zh": "营运商"}
    __i18n_fields__ = {"name"}
    __search_fields__ = {"name", "slug"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    portal: Mapped[str | None] = mapped_column(String, nullable=True)
    noc_contact: Mapped[list[str | None] | None] = mapped_column(ARRAY(String), nullable=True)
    admin_contact: Mapped[list[str | None]] = mapped_column(ARRAY(String), nullable=True)
    comments: Mapped[str | None]
    circuit: Mapped[list["Circuit"]] = relationship(
        back_populates="isp",
    )
    asn: Mapped[list["ASN"]] = relationship(secondary="isp_asn", back_populates="isp")


class ISPASN(Base):
    __tablename__ = "isp_asn"
    isp_id: Mapped[int] = mapped_column(ForeignKey("isp.id"), primary_key=True)
    asn_id: Mapped[int] = mapped_column(ForeignKey("asn.id"), primary_key=True)
