from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from src.core.database.base import Base
from src.core.database.mixins import AuditLogMixin, AuditUserMixin
from src.core.database.types import (
    PgIpAddress,
    PgIpInterface,
    date_optional,
    i18n_name,
    int_pk,
)
from src.features._types import IPvAnyAddress, IPvAnyInterface
from src.features.consts import CircuitStatus

if TYPE_CHECKING:
    from src.features.dcim.models import Device, Interface
    from src.features.intend.models import CircuitType
    from src.features.ipam.models import ASN
    from src.features.org.models import CircuitContact, Site

__all__ = ("Circuit", "ISP", "ISPASN")


class Circuit(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "circuit"
    __visible_name__ = {"en_US": "Circuit", "zh_CN": "线路"}
    __search_fields__ = {"name", "slug", "cid"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    cid: Mapped[str | None] = mapped_column(unique=True)
    status: Mapped[CircuitStatus] = mapped_column(ChoiceType(CircuitStatus))
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
    circuit_type: Mapped["CircuitType"] = relationship(back_populates="circuit")
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
    circuit_contact: Mapped["CircuitContact"] = relationship(backref="circuit", passive_deletes=True)


class ISP(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "isp"
    __visible_name__ = {"en_US": "ISP", "zh_CN": "营运商"}
    __i18n_fields__ = {"name"}
    __search_fields__ = {"name", "slug"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    account: Mapped[str | None]
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
