from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from netsight.core.database import Base
from netsight.core.database.mixins import AuditUserMixin
from netsight.core.database.types import bool_false, bool_true, int_pk


class Template(Base, AuditUserMixin):
    __tablename__ = "template"

    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str | None]
    template_id: Mapped[int]
    discovery_ospf_id: Mapped[int | None]
    discovery_bgp_id: Mapped[int | None]


class Monitor(Base, AuditUserMixin):
    __tablename__ = "monitor"

    id: Mapped[int_pk]
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="RESTRICT"))
    template_id: Mapped[int] = mapped_column(ForeignKey("template.id", ondelete="RESTRICT"))
    enable_monitor: Mapped[bool_true]
    enable_ospf: Mapped[bool_false]
    enable_bgp: Mapped[bool_false]
