import sqlalchemy.types as types
from fastapi import Request
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, JSON, UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
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


class AuditLog:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    # user_id = Column(
    #     Integer, ForeignKey("auth_user.id", ondelete="SET NULL"), nullable=True
    # )
    # auth_user = relationship("User")
    email = Column(String, nullable=False)
    request_id = Column(UUID, nullable=False)
    action = Column(
        ENUM("create", "update", "delete", name="audit_action", create_type=False),
        nullable=False,
    )
    pre_change_data = Column(JSON, nullable=True)
    post_change_data = Column(JSON, nullable=True)

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
                audit_log_id=Column(Integer, ForeignKey("%s.id" % cls.__tablename__)),
                audit_log=relationship(cls),
            ),
        )
        return relationship(cls.AuditLog)
