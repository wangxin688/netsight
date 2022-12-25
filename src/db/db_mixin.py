import sqlalchemy.types as types
from asgi_correlation_id import correlation_id
from fastapi import Request
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, event, inspect
from sqlalchemy.dialects.postgresql import ENUM, JSON, UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import class_mapper, relationship
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.sql import func

from src.db.db_base import Base


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TimestampSingleMixin:
    created_at = Column(DateTime(timezone=True), default=func.now())


class NameMixin:
    name = Column(String, nullable=False, unique=True, index=True)
    # slug = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    # @staticmethod
    # def _slug(mapper, connection, target):
    #     if target.slug is not None:
    #         target.slug = slugify(target.name)

    # @classmethod
    # def __declare_last__(cls):
    #     event.listen(cls, "before_insert", cls._slug, propagate=True)


class FileColumn(types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify a File Column
    """

    impl = types.Text


class ImageColumn(types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify an Image Column
    """

    impl = types.Text

    def __init__(self, thumbnail_size=(20, 20, True), size=(100, 100, True), **kw):
        types.TypeDecorator.__init__(self, **kw)
        self.thumbnail_size = thumbnail_size
        self.size = size


def get_object_changes(obj):
    """Given a model instance, returns dict of pending
    changes waiting for database flush/commit.

    e.g. {
        'some_field': {
            'before': *SOME-VALUE*,
            'after': *SOME-VALUE*
        },
        ...
    }
    """
    inspection = inspect(obj)
    changes = {}
    for attr in class_mapper(obj.__class__).column_attrs:
        if getattr(inspection.attrs, attr.key).history.has_changes():
            if get_history(obj, attr.key)[2]:
                before = get_history(obj, attr.key)[2].pop()
                after = getattr(obj, attr.key)
                if before != after:
                    if before or after:
                        changes[attr.key] = {"before": before, "after": after}
    return changes


class AuditLog:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    request_id = Column(UUID, nullable=False)
    action = Column(
        ENUM("create", "update", "delete", name="audit_action", create_type=False),
        nullable=False,
    )
    change_data = Column(JSON, nullable=False)

    @declared_attr
    def user_id(cls):
        return Column(
            Integer,
            ForeignKey("auth_user.id", ondelete="SET NULL"),
            default=cls.get_user_id,
            nullable=True,
        )

    @declared_attr
    def auth_user(cls):
        return relationship("User")

    @classmethod
    def get_user_id(cls, request: Request):
        try:
            return request.state.current_user.id
        except Exception:
            return None


class AuditLogMixin:
    """Use generic association which persists association objects within
    individual tables. each one generates to persist those objects on behalf of
    a particular parent class.
    Since a lot of objects are created and change logs are bottleneck in our env.
    I strongly agree with zzzeek(sqlalchemy author) that django ROR is not much good
    choice for huge data. It's better to separate tables by objects for better performance and management.
    Ses: https://stackoverflow.com/questions/17703239/sqlalchemy-generica-foreign-key-like-in-django-orm
    """

    @declared_attr
    def audit_log(cls):
        cls.AuditLog = type(
            "%sAuditLog" % cls.__name__,
            (AuditLog, Base),
            dict(
                __tablename__="%s_audit_log" % cls.__tablename__,
                parent_id=Column(Integer, ForeignKey("%s.id" % cls.__tablename__)),
                audit_log=relationship(cls, viewonly=True),
            ),
        )
        # return relationship(cls.AuditLog, cascade="all, delete")
        # if not keeping audit log, remove log_delete event and user cascade delete
        # TODO: if not set cascade, enable background housekeeping for user choices
        return relationship(cls.AuditLog)

    @classmethod
    def log_create(cls, mapper, connection, target):
        target.audit_log.append(
            cls.AuditLog(
                request_id=correlation_id.get(),
                action="create",
                change_data=target.dict(),
            )
        )

    @classmethod
    def log_update(cls, mapper, connection, target):
        change_data = get_object_changes(target)
        target.audit_log.append(
            cls.AuditLog(
                request_id=correlation_id.get(),
                action="update",
                change_data=change_data,
            )
        )

    @classmethod
    def log_delete(cls, mapper, connection, target):
        target.audit_log.append(
            cls.AuditLog(
                request_id=correlation_id.get(),
                action="delete",
                change_data=target.dict(),
            )
        )

    @classmethod
    def __declare_last__(cls):
        # https://docs.sqlalchemy.org/en/14/orm/events.html
        # propagate=False¶ – When True, the event listener should be applied to all inheriting
        # mappers and/or the mappers of inheriting classes, as well as any mapper which is the target of this listener.
        event.listen(cls, "after_insert", cls.log_create, propagate=True)
        event.listen(cls, "after_update", cls.log_update, propagate=True)
        event.listen(cls, "after_delete", cls.log_delete, propagate=True)
