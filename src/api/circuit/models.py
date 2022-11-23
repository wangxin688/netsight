from sqlalchemy import (
    TEXT,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, TimestampMixin

__all__ = ("CircuitType", "Circuit", "CircuitTermination", "Provider")


class CircuitType(Base, NameMixin):
    __tablename__ = "circuit_type"
    id = Column(Integer, primary_key=True)
    circuit = relationship(
        "Circuit", back_populates="circuit_type", passive_deletes=True
    )


class Circuit(Base, NameMixin, TimestampMixin):
    __tablename__ = "circuit"
    id = Column(Integer, primary_key=True)
    cid = Column(String, unique=True, nullable=True)
    provider_id = Column(
        Integer, ForeignKey("circuit_provider.id", ondelete="SET NULL"), nullable=True
    )

    circuit_provider = relationship(
        "Provider",
        back_populates="circuit",
        overlaps="circuit",
    )
    status = Column(String, nullable=False)
    circuit_type_id = Column(
        Integer, ForeignKey("circuit_type.id", ondelete="SET NULL"), nullable=True
    )
    circuit_type = relationship(
        "CircuitType", back_populates="circuit", overlaps="circuit"
    )
    tenant_id = Column(
        Integer, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=True
    )
    tenant = relationship("Tenant", back_populates="circuit", overlaps="circuit")
    install_date = Column(DateTime(timezone=True), nullable=True)
    purchase_term = Column(String, nullable=True)
    commit_rate = Column(Integer, nullable=True, comment="Mbps")
    comments = Column(TEXT, nullable=True)
    vendor_available_ip = Column(ARRAY(String), nullable=True)
    vendor_available_gateway = Column(ARRAY(String), nullable=True)
    contact = relationship(
        "Contact",
        secondary="circuit_contact_link",
        overlaps="circuit",
        back_populates="circuit",
    )
    circuit_termination = relationship(
        "CircuitTermination", back_populates="circuit", passive_deletes=True
    )


class CircuitTermination(Base):
    __tablename__ = "circuit_termination"
    __table_args__ = (UniqueConstraint("circuit_id", "term_side"),)
    id = Column(Integer, primary_key=True)
    term_side = Column(String, nullable=False)
    circuit_id = Column(
        Integer, ForeignKey("circuit.id", ondelete="SET NULL"), nullable=True
    )
    circuit = relationship(
        "Circuit",
        back_populates="circuit_termination",
        overlaps="circuit_termination",
    )
    # interface_id
    # interfaces


class Provider(Base, NameMixin):
    __tablename__ = "circuit_provider"
    id = Column(Integer, primary_key=True)
    asn = Column(String, nullable=True)
    account = Column(String, nullable=True)
    portal = Column(String, nullable=True)
    noc_contact = Column(ARRAY(String), nullable=True)
    admin_contact = Column(ARRAY(String), nullable=True)
    comments = Column(TEXT, nullable=True)
    circuit = relationship(
        "Circuit",
        back_populates="circuit_provider",
        overlaps="circuit_provider",
    )
