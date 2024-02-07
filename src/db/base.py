from typing import Any, ClassVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import DeclarativeBase

from src._types import VisibleName


class Base(DeclarativeBase):
    __visible_name__: ClassVar[VisibleName] = {"en_US": "base", "zh_CN": "base"}
    __search_fields__: ClassVar[set[str]] = set()
    __i18n_fields__: ClassVar[set[str]] = set()
    __order_by__: ClassVar[set[str]] = {"id"}
    __org__: ClassVar[bool] = False

    def dict(self, exclude: set[str] | None = None, native_dict: bool = False) -> dict[str, Any]:
        """Return dict representation of model."""
        if not native_dict:
            return jsonable_encoder(self, exclude=exclude)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude}

    # @declared_attr
    # def org_id(self)->Mapped[int | None]:
    # # use to extend multi-organization support.
    #     if self.__org__:
    #         return mapped_column(ForeignKey("organization.id", ondelete="CASCADE"), nullable=True)
