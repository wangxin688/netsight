import asyncio
import logging

from sqlalchemy import text

from app.db.database import sessionmanager


async def create_db_extensions() -> None:
    async with sessionmanager.session() as session:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS hstore;"))
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        await session.commit()
        logging.getLogger().setLevel(logging.INFO)
        logging.info("Init db extensions success")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db_extensions())
