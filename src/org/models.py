from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types import ChoiceType

from src.consts import LocationStatus, LocationType, SiteStatus
from src.db import Base
from src.db.db_types import int_pk
from src.db.mixins import AuditLogMixin

if TYPE_CHECKING:
    from src.db import ASN

__all__ = ("SiteGroup", "Site", "Location", "Contact", "ContactRole", "SiteContact", "CircuitContact")


class SiteGroup(Base, AuditLogMixin):
    """A aggregation of site or a set of data centor(available zone).
    site group can be used to manage the configuration/security/intend policy
    for the sites under this group.
    """

    __tablename__ = "site_group"
    __search_fields__ = {"name", "slug"}
    __visible_name__ = {"en_US": "Site Group", "zh_CN": "站点组"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    site: Mapped[list["Site"]] = relationship(back_populates="site_group")


class Site(Base, AuditLogMixin):
    """Office, Campus or data center"""

    __tablename__ = "site"
    __search_fields__ = {"name", "site_code", "physical_address"}
    __visible_name__ = {"en_US": "Site", "zh_CN": "站点"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    site_code: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[SiteStatus] = mapped_column(ChoiceType(SiteStatus))
    facility_code: Mapped[str | None]
    time_zone: Mapped[str | None]
    country: Mapped[str | None]
    city: Mapped[str | None]
    address: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    classification: Mapped[str | None]
    comments: Mapped[str | None]
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey(SiteGroup.id, ondelete="RESTRICT"))
    site_group: Mapped["SiteGroup"] = relationship(back_populates="site")
    asn: Mapped[list["ASN"]] = relationship(secondary="site_asn", back_populates="site")
    site_contact: Mapped[list["SiteContact"]] = relationship(backref="site", passive_deletes=True)


class Location(Base, AuditLogMixin):
    """a sub location of site, like building, floor, idf, mdf and etc"""

    __tablename__ = "location"
    __table_args__ = (UniqueConstraint("site_id", "name"),)
    __visible_name__ = {"en_US": "Location", "zh_CN": "位置"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    location_type: Mapped[LocationType] = mapped_column(ChoiceType(LocationType))
    description: Mapped[str | None]
    status: Mapped[LocationStatus] = mapped_column(ChoiceType(LocationStatus))
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="location", passive_deletes=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(id))
    children: Mapped[list["Location"]] = relationship(
        cascade="all, delete-orphan",
        back_populates="parent",
        remote_side=[id],
        collection_class=attribute_mapped_collection("name"),
        single_parent=True,
    )
    parent: Mapped["Location"] = relationship(back_populates="children", remote_side=[parent_id])


class Contact(Base, AuditLogMixin):
    __tablename__ = "contact"
    __visible_name__ = {"en_US": "Contact", "zh_CN": "联系人"}

    id: Mapped[int_pk]
    name: Mapped[str]
    avatar: Mapped[str | None]
    email: Mapped[str | None]
    phone: Mapped[str | None]


class ContactRole(Base, AuditLogMixin):
    __tablename__ = "contact_role"
    __visible_name__ = {"en_US": "Contact Role", "zh_CN": "联系人角色"}
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str]


class SiteContact(Base):
    __tablename__ = "site_contact"
    id: Mapped[int_pk]
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id", ondelete="RESTRICT"))
    contact: Mapped["Contact"] = relationship(backref="site_contact")
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    contact_role_id: Mapped[int] = mapped_column(ForeignKey("contact_role.id", ondelete="RESTRICT"))
    contact_role: Mapped["ContactRole"] = relationship(backref="site_contact")


class CircuitContact(Base):
    __tablename__ = "circuit_contact"
    id: Mapped[int_pk]
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id", ondelete="RESTRICT"))
    contact: Mapped["Contact"] = relationship(backref="circuit_contact")
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuit.id", ondelete="CASCADE"))
    contact_role_id: Mapped[int] = mapped_column(ForeignKey("contact_role.id", ondelete="RESTRICT"))
    contact_role: Mapped["ContactRole"] = relationship(backref="circuit_contact")


SiteGroup.site_count = column_property(
    select(func.count(Site.id)).where(Site.site_group_id == id).correlate_except(SiteGroup).scalar_subquery(),
    deferred=True,
)
