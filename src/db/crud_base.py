from typing import Generic, List, Sequence, Type, TypeVar

from pydantic import UUID4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.base import BaseModel
from src.db.db_base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(
        self, session: AsyncSession, id: int | UUID4, options: Sequence = None
    ) -> ModelType | None:
        result: ModelType | None = await session.get(self.model, id, options=options)
        return result

    async def get_multi(
        self, session: AsyncSession, ids: List[int] | List[UUID4]
    ) -> List[ModelType] | None:
        results: List[ModelType] | None = (
            (await session.execute(select(self.model).where(self.model.id.in_(ids))))
            .scalars()
            .all()
        )
        return results

    async def delete(self, session: AsyncSession, id: int | UUID4) -> ModelType | None:
        result: ModelType | None = await session.get(self.model, id)
        if result is not None:
            await session.delete(result)
            await session.commit()
        return result

    async def delete_multi(
        self, session: AsyncSession, ids: List[int] | List[UUID4]
    ) -> List[ModelType] | None:
        results: List[ModelType] | None = (
            (await session.execute(select(self.model).where(self.model.id.in_(ids))))
            .scalars()
            .all()
        )
        if results is not None:
            for result in results:
                await session.delete(result)
            await session.commit()
        return results

    async def create(
        self, session: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        new_obj = self.model(**obj_in.dict())  # type: ignore
        session.add(new_obj)
        await session.commit()
        await session.flush(new_obj)
        return new_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        excludes: set = None
    ) -> ModelType:
        await session.execute(
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(obj_in.dict(exclude_none=True, exclude=excludes))
        ).execute_options(synchronize_session="fetch")
        await session.commit()
        return db_obj
