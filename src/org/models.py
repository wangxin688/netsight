from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from src.consts import LocationStatus, SiteStatus
from src.db._types import IntegerEnum, int_pk
from src.db.base import Base
from src.db.mixins import AuditLogMixin, AuditTimeMixin

if TYPE_CHECKING:
    from src.ipam.models import ASN


class SiteGroup(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "site_group"
    __search_fields__ = {"name", "slug"}
    __visible_name__ = {"en_US": "Site Group", "zh_CN": "站点组"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    site: Mapped[list["Site"]] = relationship(back_populates="site_group")


class Site(Base, AuditTimeMixin, AuditLogMixin):
    __tablename__ = "site"
    __search_fields__ = {"name", "site_code", "physical_address"}
    __visible_name__ = {"en_US": "Site", "zh_CN": "站点"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    site_code: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[SiteStatus] = mapped_column(IntegerEnum(SiteStatus))
    facility_code: Mapped[str | None]
    time_zone: Mapped[str | None]
    country: Mapped[str | None]
    city: Mapped[str | None]
    address: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    classification: Mapped[str | None]
    comments: Mapped[str | None]
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey(SiteGroup.id, ondelete="RESTRIC"))
    site_group: Mapped["SiteGroup"] = relationship(backref="site")
    asn: Mapped[list["ASN"]] = relationship(secondary="site_asn", back_populates="site")


class Location(Base, AuditTimeMixin, AuditLogMixin):
    """a sub location of site, like building, floor, idf, mdf and etc"""

    __tablename__ = "location"
    __table_args__ = (UniqueConstraint("site_id", "name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    location_type: Mapped[int]
    description: Mapped[str | None]
    status: Mapped[LocationStatus] = mapped_column(IntegerEnum(LocationStatus))
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="location", passive_deletes=True)
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
