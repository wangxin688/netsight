"""_summary_: sqlalchemy sql generator
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class SqlalchemyGenSQL:
    async def commit(self, session: AsyncSession):
        await session.flush()
        await session.commit()

    async def delete(self, session: AsyncSession, data: Any):
        await session.delete(data)

    def update_model(self, data, update_args: dict):
        for key, value in update_args.items():
            setattr(data, key, value)
        return data

    @staticmethod
    async def async_rollback(session: AsyncSession):
        await session.rollback()

    def _update(self, db_result, update_args: dict, update_one: bool):
        if not isinstance(db_result, list):
            db_result = [
                db_result,
            ]
        tmp = []
        for _item in db_result:
            tmp.append(self.update_model(_item, update_args=update_args))

        if not update_one:
            db_result = tmp
        else:
            (db_result,) = tmp
        return db_result

    async def update(
        self, *, db_result, update_args, session: AsyncSession, update_one: bool
    ):
        result = self._update(db_result, update_args, update_one)
        await self.commit(session)
        return result
