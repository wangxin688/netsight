from datetime import datetime
from typing import List, Literal, Optional

from sqlalchemy import TEXT, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.dcim import models as dcim_models
from src.app.netsight import models as netsight_models
from src.db.db_base import Base
from src.db.db_mixin import AuditLogMixin, NameMixin, TimestampMixin

__all__ = ("CircuitType", "Circuit", "CircuitTermination", "Provider")


class CircuitType(Base):
    __tablename__ = "circuit_type"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    circuit: Mapped[List["Circuit"]] = relationship("Circuit", back_populates="circuit_type", passive_deletes=True)


class Circuit(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "circuit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cid: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("circuit_provider.id", ondelete="SET NULL"), nullable=True
    )

    circuit_provider: Mapped["Provider"] = relationship(
        "Provider", back_populates="circuit", overlaps="circuit", uselist=False
    )
    status: Mapped[Literal["Planning", "Active", "Provisioning", "Offline"]] = mapped_column(
        ENUM(
            "Planning",
            "Active",
            "Provisioning",
            "Offline",
            name="circuit_status",
            create_type=False,
        ),
        nullable=False,
    )
    circuit_type_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("circuit_type.id", ondelete="SET NULL"), nullable=True
    )
    circuit_type: Mapped["CircuitType"] = relationship(
        "CircuitType", back_populates="circuit", overlaps="circuit", uselist=False
    )
    install_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    purchase_term: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    commit_rate: Mapped[int] = mapped_column(Integer, nullable=True, comment="Mbps")
    comments: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    vendor_available_ip: Mapped[List[INET | None]] = mapped_column(ARRAY(INET), nullable=True)
    vendor_available_gateway: Mapped[List[INET | None]] = mapped_column(ARRAY(INET), nullable=True)
    contact: Mapped[List["netsight_models.Contact"]] = relationship(
        "Contact", secondary="circuit_contact_link", overlaps="circuit", back_populates="circuit"
    )
    circuit_termination: Mapped[List["CircuitTermination"]] = relationship(
        "CircuitTermination", back_populates="circuit", passive_deletes=True
    )


class CircuitTermination(Base):
    __tablename__ = "circuit_termination"
    __table_args__ = (UniqueConstraint("circuit_id", "term_side"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    term_side: Mapped[Literal["Termination_Side_A", "Termination_Side_Z"]] = mapped_column(
        ENUM(
            "Termination_Side_A",
            "Termination_Side_Z",
            name="termination",
            create_type=False,
        )
    )
    circuit_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("circuit.id", ondelete="SET NULL"), nullable=True
    )
    circuit: Mapped[Circuit] = relationship(
        "Circuit",
        back_populates="circuit_termination",
        overlaps="circuit_termination",
    )
    connection_type: Mapped[Literal["WAN", "LAN"]] = mapped_column(
        ENUM(
            "WAN" "LAN",
            name="connection_type",
            create_type=True,
        ),
        nullable=False,
    )
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("dcim_site.id", ondelete="CASCADE"))
    dcim_site: Mapped["dcim_models.Site"] = relationship(
        "Site", back_populates="circuit_termination", overlaps="circuit_termination"
    )
    device_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("dcim_device.id", ondelete="SET NULL"), nullable=True
    )
    dcim_device: Mapped["dcim_models.Device"] = relationship(
        "Device", back_populates="circuit_termination", overlaps="circuit_termination"
    )
    interface_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("dcim_interface.id", ondelete="SET NULL"), nullable=True
    )
    dcim_interface: Mapped["dcim_models.Interface"] = relationship(
        "Interface",
        back_mapped_columntes="circuit_termination",
        overlaps="circuit_termination",
    )


class Provider(Base):
    __tablename__ = "circuit_provider"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    asn: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    account: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    portal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    noc_contact: Mapped[Optional[List[str | None]]] = mapped_column(ARRAY(String), nullable=True)
    admin_contact: Mapped[List[str | None]] = mapped_column(ARRAY(String), nullable=True)
    comments: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    circuit: Mapped[Circuit] = relationship(
        "Circuit",
        back_populates="circuit_provider",
        overlaps="circuit_provider",
    )
