from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base
from src.db.db_types import EncryptedString, int_pk
from src.db.mixins import AuditLogMixin

if TYPE_CHECKING:
    from src.db import Platform


class BaseLineConfig(Base, AuditLogMixin):
    __tablename__ = "baseline_config"
    __visible_name__ = {"en_US": "Baseline Configuration", "zh_CN": "基线配置"}
    id: Mapped[int_pk]
    aaa_server: Mapped[str | None] = mapped_column(EncryptedString())
    dhcp_server: Mapped[str | None] = mapped_column(EncryptedString())
    dns_server: Mapped[str | None] = mapped_column(EncryptedString())
    ntp_server: Mapped[str | None] = mapped_column(EncryptedString())
    syslog_server: Mapped[str | None] = mapped_column(EncryptedString())
    netflow_server: Mapped[str | None] = mapped_column(EncryptedString())
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey("site_group.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_group_id: Mapped[int | None] = mapped_column(ForeignKey("device_group.id", ondelete="CASCADE"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class DeviceCredential(Base, AuditLogMixin):
    __tablename__ = "device_credential"
    __visible_name__ = {"en_US": "Baseline Configuration", "zh_CN": "基线配置"}
    id: Mapped[int_pk]
    cli: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv2_read: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv2_write: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv3: Mapped[str | None] = mapped_column(EncryptedString())
    http_read: Mapped[str | None] = mapped_column(EncryptedString())
    http_write: Mapped[str | None] = mapped_column(EncryptedString())
    site_group_id: Mapped[int | None] = mapped_column(ForeignKey("site_group.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_group_id: Mapped[int | None] = mapped_column(ForeignKey("device_group.id", ondelete="CASCADE"))
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
    platform: Mapped["Platform"] = relationship(back_populates="textfsm_template")


class JinjaTemplate(Base):
    __tablename__ = "jinja_template"
    __visible_name__ = {"en_US": "Jinja Template", "zh_CN": "Jinja模板"}
    id: Mapped[int_pk]
    name: Mapped[str]
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id", ondelete="RESTRICT"))
    platform: Mapped["Platform"] = relationship(back_populates="jinja_template")
