from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base import Base
from src.core.database.mixins import AuditLogMixin
from src.core.database.types import EncryptedString, int_pk

if TYPE_CHECKING:
    from src.features.dcim.models import Platform

__all__ = ("BaseLineConfig", "AuthCredential", "WLANConfig", "TextFsmTemplate", "JinjaTemplate")


class BaseLineConfig(Base, AuditLogMixin):
    __tablename__ = "baseline_config"
    __visible_name__ = {"en_US": "Baseline Configuration", "zh_CN": "基线配置"}
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


class AuthCredential(Base, AuditLogMixin):
    __tablename__ = "auth_credential"
    __visible_name__ = {"en_US": "Auth Crendential", "zh_CN": "认证凭证"}
    id: Mapped[int_pk]
    cli: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv2_community: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv3: Mapped[str | None] = mapped_column(EncryptedString())
    http_read: Mapped[str | None] = mapped_column(EncryptedString())
    http_write: Mapped[str | None] = mapped_column(EncryptedString())
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey("site_group.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class WLANConfig(Base):
    __tablename__ = "wlan_config"
    __visible_name__ = {"en_US": "WLAN Configuration", "zh_CN": "无线配置"}
    id: Mapped[int_pk]


class TextFsmTemplate(Base):
    __tablename__ = "textfsm_template"
    __visible_name__ = {"en_US": "TextFSM Template", "zh_CN": "TextFSM模板"}
    id: Mapped[int_pk]
    name: Mapped[str]
    commonad: Mapped[str]
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(backref="textfsm_template")


class JinjaTemplate(Base):
    __tablename__ = "jinja_template"
    __visible_name__ = {"en_US": "Jinja Template", "zh_CN": "Jinja模板"}
    id: Mapped[int_pk]
    name: Mapped[str]
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(backref="jinja_template")
