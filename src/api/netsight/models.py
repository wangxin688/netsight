from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, TimestampMixin

__all__ = (
    "TenantASNLink",
    "TenantContactLink",
    "SiteContact",
    "CircuitContact",
    "Tenant",
    "Contact",
)


class TenantASNLink(Base):
    __tablename__ = "tenant_ipam_asn_link"
    tenant_id = Column(Integer, ForeignKey("tenant.id"), primary_key=True)
    asn_id = Column(Integer, ForeignKey("ipam_asn.id"), primary_key=True)


class TenantContactLink(Base):
    __tablename__ = "tenant_contact_link"
    tenant_id = Column(Integer, ForeignKey("tenant.id"), primary_key=True)
    contact_id = Column(Integer, ForeignKey("contact.id"), primary_key=True)


class SiteContact(Base):
    __tablename__ = "dcim_site_contact_link"
    site_id = Column(Integer, ForeignKey("dcim_site.id"), primary_key=True)
    contact_id = Column(Integer, ForeignKey("contact.id"), primary_key=True)


class CircuitContact(Base):
    __tablename__ = "circuit_contact_link"
    __tablename__ = "tenant_asn_link"
    circuit_id = Column(Integer, ForeignKey("circuit.id"), primary_key=True)
    contact_id = Column(Integer, ForeignKey("contact.id"), primary_key=True)


class Tenant(Base, NameMixin, TimestampMixin):
    __tablename__ = "tenant"
    id = Column(Integer, primary_key=True)
    dcim_site = relationship(
        "Site", back_populates="tenant", cascade="all, delete", passive_deletes=True
    )
    ipam_asn = relationship(
        "ASN", secondary="tenant_asn_link", overlaps="tenant", back_populates="tenant"
    )
    contact = relationship(
        "Contact",
        secondary="tenant_contact_link",
        overlaps="tenant",
        back_populates="tenant",
    )
    ipam_vrf = relationship("VRF", back_populates="tenant", passive_deletes=True)
    ipam_block = relationship("Block", back_populates=True, passive_deletes=True)
    ipam_prefix = relationship("Prefix", back_populates="tenant", passive_deletes=True)
    ipam_ip_address = relationship(
        "IPAddress", back_populates="tenant", passive_deletes=True
    )
    ipam_route_target = relationship(
        "RouteTarget", back_populates="tenant", passive_deletes=True
    )
    ipam_vlan = relationship("VLAN", back_populates="tenant", passive_deletes=True)
    circuit = relationship("Circuit", back_populates="tenant", passive_deletes=True)


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    tenant = relationship(
        "Tenant",
        secondary="tenant_contact_link",
        overlaps="contact",
        back_populates="contact",
    )
    dcim_site = relationship(
        "Site",
        secondary="dcim_site_contact_link",
        overlaps="contact",
        back_populates="contact",
    )
    circuit = relationship(
        "Circuit",
        secondary="circuit_link",
        overlaps="contact",
        back_populates="contact",
    )
