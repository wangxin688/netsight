from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netsight.core.database import Base
from netsight.core.database.mixins import AuditLogMixin, AuditUserMixin
from netsight.core.database.types import EncryptedString, int_pk

if TYPE_CHECKING:
    from netsight.features.dcim.models import Platform

__all__ = ("BaseLineConfig", "AuthCredential", "TextFsmTemplate", "JinjaTemplate")


class BaseLineConfig(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "baseline_config"
    __visible_name__ = {"en": "Baseline Configuration", "zh": "基线配置"}
    id: Mapped[int_pk]
    aaa_server: Mapped[list[str] | None] = mapped_column(ARRAY(String, dimensions=1))
    dhcp_server: Mapped[list[str] | None] = mapped_column(ARRAY(String, dimensions=1))
    dns_server: Mapped[list[str] | None] = mapped_column(ARRAY(String, dimensions=1))
    ntp_server: Mapped[list[str] | None] = mapped_column(ARRAY(String, dimensions=1))
    syslog_server: Mapped[list[str] | None] = mapped_column(ARRAY(String, dimensions=1))
    netflow_server: Mapped[list[str] | None] = mapped_column(ARRAY(String, dimensions=1))
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey("site_group.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class AuthCredential(Base, AuditUserMixin, AuditLogMixin):
    __tablename__ = "auth_credential"
    __visible_name__ = {"en": "Auth Crendential", "zh": "认证凭证"}
    id: Mapped[int_pk]
    cli: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv2_community: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv3: Mapped[str | None] = mapped_column(EncryptedString())
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey("site_group.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class TextFsmTemplate(Base, AuditUserMixin):
    __tablename__ = "textfsm_template"
    __visible_name__ = {"en": "TextFSM Template", "zh": "TextFSM模板"}
    id: Mapped[int_pk]
    name: Mapped[str]
    template: Mapped[str]
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(backref="textfsm_template")


class JinjaTemplate(Base, AuditUserMixin):
    __tablename__ = "jinja_template"
    __visible_name__ = {"en": "Jinja Template", "zh": "Jinja模板"}
    id: Mapped[int_pk]
    name: Mapped[str]
    template: Mapped[str]
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(backref="jinja_template")
