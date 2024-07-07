from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ChoiceType

from src.core.database import Base
from src.core.database.mixins import AuditTimeMixin, AuditUserMixin
from src.core.database.types import DateTimeTZ, bool_false, bool_true, i18n_name, int_pk
from src.core.utils.processors import format_duration
from src.features.alert.consts import (
    AlertSeverityType,
    AlertStatusType,
    EventOperationType,
    NotificationChannelType,
    NotificationResultType,
)

if TYPE_CHECKING:
    from src.features.admin.models import User
    from src.features.dcim.models import Device, Interface
    from src.features.org.models import Site

__all__ = (
    "Alert",
    "AlertUser",
    "Event",
    "EventGroup",
    "EventOperation",
    "Inhibitor",
    "Correlation",
    "Subscription",
    "NotificationRecord",
    "EventOperation",
)


class AlertUser(Base, AuditUserMixin):
    __tablename__ = "alert_user"
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(backref="alert_user")
    online_date: Mapped[list[dict]] = mapped_column(JSON)


class Alert(Base, AuditTimeMixin):
    __tablename__ = "alert"
    __visible_name__ = {"en_US": "AlertMeta", "zh_CN": "告警定义"}
    id: Mapped[int_pk]
    name: Mapped[i18n_name] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[i18n_name]
    possible_impacts: Mapped[i18n_name]
    remediation_suggestion: Mapped[i18n_name]
    references: Mapped[str | None]
    severity: Mapped[str] = mapped_column(
        ChoiceType(AlertSeverityType, impl=String()), default=AlertSeverityType.P4.value
    )


class EventMixin:
    status: Mapped[AlertStatusType] = mapped_column(
        ChoiceType(AlertStatusType, impl=String()), default=AlertStatusType.FIRERING.value
    )
    started_at: Mapped[datetime] = mapped_column(DateTimeTZ, default=func.now())
    resolved_at: Mapped[datetime] = mapped_column(DateTimeTZ, nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTimeTZ, nullable=True)
    acknowledged_by: Mapped[int | None] = mapped_column(ForeignKey("alert_user.id"), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTimeTZ, nullable=True)
    closed_by: Mapped[int | None] = mapped_column(ForeignKey("alert_user.id"), nullable=True)
    severity: Mapped[str] = mapped_column(
        ChoiceType(AlertSeverityType, impl=String()), default=AlertSeverityType.P4.value
    )

    @property
    def duration(self) -> str:
        if self.status == AlertStatusType.FIRERING.value:
            return format_duration(int(datetime.now(tz=UTC).timestamp() - self.started_at.timestamp()))
        return format_duration(int(self.resolved_at.timestamp() - self.started_at.timestamp()))


class Event(Base, EventMixin):
    __tablename__ = "event"
    __visible_name__ = {"en_US": "AlertEvent", "zh_CN": "告警事件"}
    id: Mapped[int_pk]
    alert_id: Mapped[int] = mapped_column(ForeignKey("alert.id", ondelete="CASCADE"))
    alert: Mapped["Alert"] = relationship(backref="event")
    event_group_id: Mapped[int | None] = mapped_column(ForeignKey("event_group.id", ondelete="CASCADE"), nullable=True)
    event_group: Mapped["EventGroup"] = relationship(back_populates="event")
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    site: Mapped["Site"] = relationship(backref="event")
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"))
    device: Mapped["Device"] = relationship(backref="event")
    device_role_id: Mapped[int]  # redundant column for performance
    platform_id: Mapped[int]  # redundant column for performance
    device_type_id: Mapped[int]  # redundant column for performance
    interface_id: Mapped[int | None] = mapped_column(ForeignKey("interface.id", ondelete="CASCADE"), nullable=True)
    interface: Mapped["Interface"] = relationship(backref="event")
    inhibitor_id: Mapped[int | None] = mapped_column(ForeignKey("inhibitor.id", ondelete="CASCADE"), nullable=True)
    inhibitor: Mapped["Inhibitor"] = relationship(backref="inhibitor")
    event_operation: Mapped[list["EventOperation"]] = relationship(
        back_populates="event", secondary="event_operation_event"
    )


class EventGroup(Base, EventMixin):
    __tablename__ = "event_group"
    __visible_name__ = {"en_US": "AlertEventGroup", "zh_CN": "告警事件组"}
    id: Mapped[int_pk]
    name: Mapped[str]
    group_key: Mapped[str | None]
    content_hash: Mapped[str | None]
    description: Mapped[str | None]
    event: Mapped[list["Event"]] = relationship(back_populates="event_group")
    event_operation: Mapped[list["EventOperation"]] = relationship(
        back_populates="event_group", secondary="event_operation_event_group"
    )


class Correlation(Base, AuditUserMixin):
    __tablename__ = "correlation"
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str | None]
    order: Mapped[int]
    source_match: Mapped[list[dict]] = mapped_column(JSON)
    target_match: Mapped[list[dict]] = mapped_column(JSON)
    equal_value: Mapped[list[str]] = mapped_column(JSON)


class Inhibitor(Base, AuditUserMixin):
    __tablename__ = "inhibitor"
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str | None]
    started_at: Mapped[datetime] = mapped_column(DateTimeTZ)
    ended_at: Mapped[datetime] = mapped_column(DateTimeTZ)
    rules: Mapped[list[dict]] = mapped_column(JSON)


class Subscription(Base, AuditUserMixin):
    __tablename__ = "subscription"
    id: Mapped[int_pk]
    name: Mapped[str]
    enable: Mapped[bool_true]
    description: Mapped[str | None]
    enable_time_range: Mapped[bool_false]
    time_range: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    group_delay: Mapped[int]
    send_repeat: Mapped[bool_false]
    repeat_interval: Mapped[int] = mapped_column(default=0)
    max_repeat: Mapped[int] = mapped_column(default=0)  # 0 means no limit
    send_resolved: Mapped[bool_false]
    channel_type: Mapped[NotificationChannelType] = mapped_column(ChoiceType(NotificationChannelType, impl=String()))
    channel_config: Mapped[dict] = mapped_column(JSON)


class NotificationRecord(Base):
    __tablename__ = "notification_record"
    id: Mapped[int_pk]
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscription.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=True)
    event_group_id: Mapped[int] = mapped_column(ForeignKey("event_group.id"), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTimeTZ, default=func.now())
    result_code: Mapped[NotificationResultType] = mapped_column(ChoiceType(NotificationResultType, impl=String()))
    result_message: Mapped[str | None]


class EventOperationEvent(Base):
    __tablename__ = "event_operation_event"
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey("event_operation.id"), primary_key=True)


class EventOperationEventGroup(Base):
    __tablename__ = "event_operation_event_group"
    event_group_id: Mapped[int] = mapped_column(ForeignKey("event_group.id"), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey("event_operation.id"), primary_key=True)


class EventOperation(Base):
    __tablename__ = "event_operation"
    id: Mapped[int_pk]
    operation_type: Mapped[EventOperationType] = mapped_column(ChoiceType(EventOperationType, impl=String()))
    comment: Mapped[str | None]
    inhibitor_id: Mapped[int | None] = mapped_column(ForeignKey("inhibitor.id"), nullable=True)
    inhibitor: Mapped["Inhibitor"] = relationship(backref="event_operation")
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("alert_user.id"), nullable=True)
    assignee: Mapped["AlertUser"] = relationship(backref="event_operation")
    created_at: Mapped[datetime] = mapped_column(DateTimeTZ, default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"))
    event: Mapped[list["Event"]] = relationship(back_populates="event_operation", secondary="event_operation_event")
    event_group: Mapped[list["EventGroup"]] = relationship(
        back_populates="event_operation", secondary="event_operation_event_group"
    )
