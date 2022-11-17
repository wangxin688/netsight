import sqlalchemy.types as types
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.register.context import correlation_id_filter
from src.utils.slugify import slugify


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TimestampSingleMixin:
    created_at = Column(DateTime(timezone=True), default=func.now())


class PrimaryKeyMixin:
    id = Column(Integer, primary_key=True)


class NameMixin:
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(String, nullable=True)

    @staticmethod
    def _slug(mapper, connection, target):
        if target.slug is not None:
            target.slug = slugify(target.name)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "after_create", cls._slug, propagate=True)


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


class AuditLogMixin:
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)

    @declared_attr
    def created_by_fk(cls):
        return Column(
            Integer, ForeignKey("user.id"), default=cls.get_user_id, nullable=False
        )

    @declared_attr
    def created_by(cls):
        return relationship(
            "User",
            primaryjoin="%s.created_by_fk == User.id" % cls.__name__,
            enable_typechecks=False,
        )

    @declared_attr
    def updated_by_fk(cls):
        return Column(
            Integer,
            ForeignKey("user.id"),
            default=cls.get_user_id,
            onupdate=cls.get_user_id,
            nullable=False,
        )

    @declared_attr
    def updated_by(cls):
        return relationship(
            "User",
            primaryjoin="%s.changed_by_fk == User.id" % cls.__name__,
            enable_typechecks=False,
        )

    @classmethod
    def get_user_id(cls):
        try:
            return correlation_id_filter.user.id
        except Exception:
            return None
