import asyncio

from sqlalchemy import text

from src.db.session import async_session


async def create_db_extensions() -> None:
    async with async_session() as session:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS hstore;"))
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        await session.commit()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db_extensions())
