import logging
from typing import Any, ClassVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app._types import VisibleName
from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    __visible_name__: ClassVar[VisibleName] = {"en_US": "base", "zh_CN": "base"}
    __search_fields__: ClassVar[set[str]] = set()
    __i18n_fields__: ClassVar[set[str]] = set()
    __order_by__: ClassVar[set[str]] = {"id"}
    __org__: ClassVar[bool] = False

    def dict(self, exclude: set[str] | None = None, native_dict: bool = False) -> dict[str, Any]:
        """Return dict representation of model."""
        exclude = exclude if exclude else set()
        if not native_dict:
            return jsonable_encoder(self, exclude=exclude)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude}

    # @declared_attr
    # def org_id(self)->Mapped[int | None]:
    # # use to extend multi-organization support.
    #     if self.__org__:
    #         return mapped_column(ForeignKey("organization.id", ondelete="CASCADE"), nullable=True)


class DatabaseSessionManager:
    def __init__(self, host: str = settings.SQLALCHEMY_DATABASE_URI) -> None:
        self.engine = create_async_engine(
            url=host,
            pool_pre_ping=True,
            future=True,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_POOL_MAX_OVERFLOW,
        )
        self.session = async_sessionmaker(self.engine, autoflush=False, expire_on_commit=False)

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()


sessionmanager = DatabaseSessionManager()
