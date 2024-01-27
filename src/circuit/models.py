from typing import TYPE_CHECKING

from sqlalchemy import TEXT, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db._types import date_optional, i18n_name, int_pk
from src.db.base import Base
from src.db.mixins import AuditLogMixin, AuditTimeMixin

if TYPE_CHECKING:
    from src.arch.models import CircuitType
    from src.dcim.models import Device, Interface
    from src.ipam.models import ASN
    from src.org.models import Site


class Circuit(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "circuit"
    __visible_name__ = {"en_US": "Circuit", "zh_CN": "线路"}
    __search_fields__ = {"name", "slug", "cid"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    cid: Mapped[str | None] = mapped_column(unique=True)
    status: Mapped[int]
    install_date: Mapped[date_optional]
    purchase_term: Mapped[str | None]
    bandwidth: Mapped[int] = mapped_column(comment="Mbps")
    comments: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    vendor_available_ip: Mapped[list[str] | None] = mapped_column(ARRAY(INET), nullable=True)
    vendor_available_gateway: Mapped[list[str] | None] = mapped_column(ARRAY(INET), nullable=True)
    isp_id: Mapped[int] = mapped_column(ForeignKey("isp.id", ondelete="RESTRICT"))
    isp: Mapped["ISP"] = relationship(backref="circuit")
    circuit_type_id: Mapped[int] = mapped_column(ForeignKey("circuit_type.id", ondelete="RESTRICT"))
    circuit_type: Mapped["CircuitType"] = relationship(backref="circuit")
    site_a_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="RESTRICT"))
    site_a: Mapped["Site"] = relationship(foreign_keys=[site_a_id], backref="circuit")
    device_a_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="RESTRICT"))
    device_a: Mapped["Device"] = relationship(foreign_keys=[device_a_id], backref="circuit")
    interface_a_id: Mapped[int] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface_a: Mapped["Interface"] = relationship(foreign_keys=[interface_a_id], backref="circuit")
    site_z_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="RESTRICT"))
    site_z: Mapped["Site"] = relationship(foreign_keys=[site_z_id], backref="circuit")
    device_z_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="RESTRICT"))
    device_z: Mapped["Device"] = relationship(foreign_keys=[device_z_id], backref="circuit")
    interface_z_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="SET NULL"))
    interface_z: Mapped["Interface"] = relationship(foreign_keys=[interface_z_id], backref="circuit")


class ISP(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "isp"
    __visible_name__ = {"en_US": "ISP", "zh_CN": "营运商"}
    __i18n_fields__ = {"name"}
    __search_fields__ = {"name", "slug"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name]
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    account: Mapped[str | None]
    portal: Mapped[str | None] = mapped_column(String, nullable=True)
    noc_contact: Mapped[list[str | None] | None] = mapped_column(ARRAY(String), nullable=True)
    admin_contact: Mapped[list[str | None]] = mapped_column(ARRAY(String), nullable=True)
    comments: Mapped[str | None]
    circuit: Mapped[list["Circuit"]] = relationship(
        back_populates="circuit_provider",
        overlaps="circuit_provider",
    )
    asn: Mapped[list["ASN"]] = relationship(secondary="isp_asn", back_populates="isp")


class ISPASN(Base):
    __tablename__ = "isp_asn"
    isp_id: Mapped[int] = mapped_column(ForeignKey("isp.id"), primary_key=True)
    asn_id: Mapped[int] = mapped_column(ForeignKey("asn.id"), primary_key=True)
