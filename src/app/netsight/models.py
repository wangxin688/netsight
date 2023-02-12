from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from src.db.db_base import Base
from src.db.db_mixin import NameMixin

__all__ = ("SiteContact", "CircuitContact", "Contact")


class Department(Base, NameMixin):
    __tablename__ = "department"
    id = id = mapped_column(Integer, primary_key=True)
    dcim_device = relationship("Device", back_populates="department", passive_deletes=True)
    server = relationship("Server", back_populates="department", passive_deletes=True)


class SiteContact(Base):
    __tablename__ = "dcim_site_contact_link"
    site_id = mapped_column(Integer, ForeignKey("dcim_site.id"), primary_key=True)
    contact_id = mapped_column(Integer, ForeignKey("contact.id"), primary_key=True)


class CircuitContact(Base):
    __tablename__ = "circuit_contact_link"
    circuit_id = mapped_column(Integer, ForeignKey("circuit.id"), primary_key=True)
    contact_id = mapped_column(Integer, ForeignKey("contact.id"), primary_key=True)


class Contact(Base):
    __tablename__ = "contact"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    email = mapped_column(String, nullable=False, unique=True)
    phone = mapped_column(String, nullable=True)
    categories = mapped_column(String, nullable=False)
    dcim_site = relationship(
        "Site",
        secondary="dcim_site_contact_link",
        overlaps="contact",
        back_populates="contact",
    )
    circuit = relationship(
        "Circuit",
        secondary="circuit_contact_link",
        overlaps="contact",
        back_populates="contact",
    )
    server = relationship("Server", back_populates="contact", passive_deletes=True)
