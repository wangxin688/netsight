from enum import StrEnum


class AlertStatusType(StrEnum):
    FIRERING = "FIRERING"
    RESOLVED = "RESOLVED"


class AlertSeverityType(StrEnum):
    P4 = "P4"
    P3 = "P3"
    P2 = "P2"
    P1 = "P1"
    P0 = "P0"


class NotificationChannelType(StrEnum):
    WEBHOOK = "WEBHOOK"
    FEISHU_PRIVATE = "FEISHU_PRIVATE"
    FEISHU_GROUP = "FEISHU_GROUP"
    DINGTALK_PRIVATE = "DINGTALK_PRIVATE"
    DINGTALK_GROUP = "DINGTALK_GROUP"
    WECHAT_PRIVATE = "WECHAT_PRIVATE"
    WECHAT_GROUP = "WECHAT_GROUP"
    SLACK_PRIVATE = "SLACK_PRIVATE"
    SLACK_GROUP = "SLACK_GROUP"
    EMAIL = "EMAIL"


class NotificationResultType(StrEnum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class EventOperationType(StrEnum):
    ACKNOWLEDGE = "ACKNOWLEDGE"
    UNACKNOWLEDGE = "UNACKNOWLEDGE"
    CLOSE = "CLOSE"
    COMMENT = "COMMENT"
    ASSIGN = "ASSIGN"
    INHIBIT = "INHIBIT"
