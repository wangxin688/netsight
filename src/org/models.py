from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from src.db._types import int_pk
from src.db.base import Base
from src.db.mixins import AuditLogMixin, AuditTimeMixin

if TYPE_CHECKING:
    from src.ipam.models import ASN


class Region(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "region"
    __search_fields__ = {"name", "slug"}
    __visible_name__ = {"en_US": "Area", "zh_CN": "区域"}
    __table_args__ = (UniqueConstraint("parent_id", "name"), UniqueConstraint("parent_id", "slug"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    slug: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(id))
    children: Mapped[list["Region"]] = relationship(
        "Region",
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )


class Site(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "site"
    __search_fields__ = {"name", "site_code", "physical_address"}
    __visible_name__ = {"en_US": "Site", "zh_CN": "站点"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    site_code: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[int]
    facility_code: Mapped[str | None]
    ipam_asn: Mapped["ASN"] = relationship(secondary="site_asn", back_populates="dcim_site")
    time_zone: Mapped[str | None]
    physical_address: Mapped[str | None]
    shipping_address: Mapped[str | None]
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    classification: Mapped[str | None]
    description: Mapped[str | None]
    region_id: Mapped[int] = mapped_column(ForeignKey(Region.id, ondelete="CASCADE"))
    region: Mapped["Region"] = relationship("Region", backref="site", passive_deletes=True)


class Location(Base, AuditTimeMixin, AuditLogMixin):
    """a sub location of site, like building, floor, idf, mdf and etc"""

    __tablename__ = "location"
    __table_args__ = (UniqueConstraint("site_id", "name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    location_type: Mapped[int]
    description: Mapped[str | None]
    status: Mapped[int]
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("dcim_site.id", ondelete="CASCADE"))
    dcim_site: Mapped["Site"] = relationship(backref="location", passive_deletes=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(id))
    children: Mapped[list["Location"]] = relationship(
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )


class Contact(Base):
    __tablename__ = "contact"
    __visible_name__ = {"en_US": "Contact", "zh_CN": "联系人"}

    id: Mapped[int_pk]
    name: Mapped[str]
    avatar: Mapped[str | None]
    email: Mapped[str | None]
    phone: Mapped[str | None]


class ContactRole(Base):
    __tablename__ = "contact_role"
    __visible_name__ = {"en_US": "Contact Role", "zh_CN": "联系人角色"}
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str]


class SiteGroup(Base):
    __tablename__ = "site_group"
    __visible_name__ = {"en_US": "Site Group", "zh_CN": "站点组"}


class SiteContact(Base):
    __tablename__ = "site_contact"
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"), primary_key=True)
    contact: Mapped["Contact"] = relationship(backref="site_contact")
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="CASCADE"))
    contact_role: Mapped["ContactRole"] = relationship(backref="contact_site", passive_deletes=True)


class CircuitContact(Base):
    __tablename__ = "circuit_contact"
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"), primary_key=True)
    contact: Mapped["Contact"] = relationship(backref="site_contact")
    circuit_id: Mapped[int] = mapped_column(ForeignKey("site.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="CASCADE"))
    contact_role: Mapped["ContactRole"] = relationship(backref="contact_site", passive_deletes=True)
