from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db._types import EncryptedString, int_pk
from src.db.base import Base
from src.db.mixins import AuditTimeMixin, AuditUserMixin


class BaseLineConfig(Base, AuditTimeMixin, AuditUserMixin):
    __tablename__ = "baseline_config"
    __visible_name__ = {"en_US": "Baseline Configuration", "zh_CN": "基线配置"}
    id: Mapped[int_pk]
    aaa_server: Mapped[str | None] = mapped_column(EncryptedString())
    dhcp_server: Mapped[str | None] = mapped_column(EncryptedString())
    dns_server: Mapped[str | None] = mapped_column(EncryptedString())
    ntp_server: Mapped[str | None] = mapped_column(EncryptedString())
    syslog_server: Mapped[str | None] = mapped_column(EncryptedString())
    netflow_server: Mapped[str | None] = mapped_column(EncryptedString())
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_group_id: Mapped[int | None] = mapped_column(ForeignKey("device_group.id", ondelete="CASCADE"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class DeviceCredential(Base, AuditTimeMixin, AuditUserMixin):
    __tablename__ = "baseline_config"
    __visible_name__ = {"en_US": "Baseline Configuration", "zh_CN": "基线配置"}
    id: Mapped[int_pk]
    cli: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv2_read: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv2_write: Mapped[str | None] = mapped_column(EncryptedString())
    snmpv3: Mapped[str | None] = mapped_column(EncryptedString())
    http_read: Mapped[str | None] = mapped_column(EncryptedString())
    http_write: Mapped[str | None] = mapped_column(EncryptedString())
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id", ondelete="CASCADE"))
    site_id: Mapped[int | None] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    device_group_id: Mapped[int | None] = mapped_column(ForeignKey("device_group.id", ondelete="CASCADE"))
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))


class WLANConfig(Base):
    __tablename__ = "wlan_config"
    __visible_name__ = {"en_US": "WLAN Configuration", "zh_CN": "无线配置"}
    id: Mapped[int_pk]


# class TtpTemplate(Base):

# class JinjaTemplate(Base):
