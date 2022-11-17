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
from src.db.db_mixin import NameMixin, PrimaryKeyMixin, TimestampMixin

__all__ = ("Circuit", "CircuitTermination")


class Circuit(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "circuits"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cid = Column(String, unique=True, nullable=True)
    provider_id = Column(
        Integer, ForeignKey("circuit_providers.id", ondelete="SET NULL"), nullable=True
    )

    circuit_providers = relationship(
        "Provider",
        back_populates="circuits",
        overlaps="circuits",
    )
    status = Column(String, nullable=False)
    circuit_type = Column(String, nullable=False)
    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    tenants = relationship("Tenant", back_populates="circuits", overlaps="circuits")
    install_date = Column(DateTime(timezone=True), nullable=True)
    purchase_term = Column(String, nullable=True)
    commit_rate = Column(Integer, nullable=True, comment="Mbps")
    comments = Column(TEXT, nullable=True)
    vendor_available_ip = Column(ARRAY(String), nullable=True)
    vendor_available_gateway = Column(ARRAY(String), nullable=True)
    contacts = relationship(
        "Contact",
        secondary="circuit_contact_link",
        overlaps="circuits",
        back_populates="circuits",
    )
    circuit_terminations = relationship(
        "CircuitTermination", back_populates="circuits", passive_deletes=True
    )


class CircuitTermination(Base):
    __tablename__ = "circuit_terminations"
    __table_args__ = (UniqueConstraint("circuit_id", "term_side"),)
    id = Column(Integer, primary_key=True)
    term_side = Column(String, nullable=False)
    circuit_id = Column(
        Integer, ForeignKey("circuits.id", ondelete="SET NULL"), nullable=True
    )
    circuits = relationship(
        "Circuit",
        back_populates="circuit_terminations",
        overlaps="circuit_terminations",
    )
    # interface_id
    # interfaces


class Provider(Base, PrimaryKeyMixin, NameMixin):
    __tablename__ = "circuit_providers"
    asn = Column(String, nullable=True)
    account = Column(String, nullable=True)
    portal = Column(String, nullable=True)
    noc_contact = Column(ARRAY(String), nullable=True)
    admin_contact = Column(ARRAY(String), nullable=True)
    comments = Column(TEXT, nullable=True)
    circuits = relationship(
        "Circuit",
        back_populates="circuit_providers",
        overlaps="circuit_providers",
    )
