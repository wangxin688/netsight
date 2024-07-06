from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types import ChoiceType

from src.core.database.base import Base
from src.core.database.mixins import AuditLogMixin, AuditUserMixin
from src.core.database.types import int_pk
from src.features.consts import LocationStatus, LocationType, SiteStatus

if TYPE_CHECKING:
    from src.features.admin.models import User
    from src.features.ipam.models import ASN

__all__ = ("SiteGroup", "Site", "Location")


class Site(Base, AuditUserMixin, AuditLogMixin):
    """Office, Campus or data center"""

    __tablename__ = "site"
    __search_fields__ = {"name", "site_code", "physical_address"}
    __visible_name__ = {"en_US": "Site", "zh_CN": "站点"}
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)
    site_code: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[SiteStatus] = mapped_column(ChoiceType(SiteStatus))
    facility_code: Mapped[str | None]
    time_zone: Mapped[int | None]
    country: Mapped[str | None]
    city: Mapped[str | None]
    address: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    classification: Mapped[str | None]
    comments: Mapped[str | None]
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey("site_group.id", ondelete="RESTRICT"))
    site_group: Mapped["SiteGroup"] = relationship(back_populates="site")
    asn: Mapped[list["ASN"]] = relationship(secondary="site_asn", back_populates="site")
    network_contact_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    it_contact_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    network_contact: Mapped["User"] = relationship(back_populates="site_network_contact")
    it_contact: Mapped["User"] = relationship(back_populates="site_it_contact")

    if TYPE_CHECKING:
        device_count: Mapped[int]
        circuit_count: Mapped[int]

    @classmethod
    def __declare_last__(cls) -> None:
        from sqlalchemy import func, or_, select

        from src.features.circuit.models import Circuit
        from src.features.dcim.models import Device

        cls.device_count = column_property(
            select(func.count(Device.id)).where(Device.site_id == cls.id).scalar_subquery(),
            deferred=True,
        )
        cls.circuit_count = column_property(
            select(func.count(Circuit.id))
            .where(or_(Circuit.site_a_id == cls.id, Circuit.site_z_id == cls.id))
            .scalar_subquery(),
            deferred=True,
        )


class SiteGroup(Base, AuditUserMixin):
    """A aggregation of site or a set of data centor(available zone).
    site group can be used to manage the configuration/security/intend policy
    for the sites under this group.
    """

    __tablename__ = "site_group"
    __search_fields__ = {"name", "slug"}
    __visible_name__ = {"en_US": "Site Group", "zh_CN": "站点组"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    site: Mapped[list["Site"]] = relationship(back_populates="site_group")
    site_count: Mapped[int] = column_property(
        select(func.count(Site.id)).where(Site.site_group_id == id).scalar_subquery(),
        deferred=True,
    )


class Location(Base, AuditUserMixin, AuditLogMixin):
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
