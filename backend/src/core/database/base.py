from typing import Any, ClassVar, TypedDict, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import DeclarativeBase


class VisibleName(TypedDict, total=True):
    en: str
    zh: str


class Base(DeclarativeBase):
    __visible_name__: ClassVar[VisibleName] = {"en": "base", "zh": "base"}
    __search_fields__: ClassVar[set[str]] = set()
    __i18n_fields__: ClassVar[set[str]] = set()

    def dict(self, exclude: set[str] | None = None, native_dict: bool = False) -> dict[str, Any]:
        """Return dict representation of model."""
        if not native_dict:
            return jsonable_encoder(self, exclude=exclude)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude}

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)

    def __str__(self) -> str:
        if hasattr(self, "name"):
            return f"{self.__class__.__name__}: {self.name}"
        return f"{type(self).__name__}:{self.id}"


ModelT = TypeVar("ModelT", bound=Base)
