from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from src.core.config import settings
from src.utils.loggers import logger

async_sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(
    async_sqlalchemy_database_uri, pool_pre_ping=True, future=True, echo=True
)
async_session: AsyncSession = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_session() -> AsyncGenerator:
    try:
        session: AsyncSession = async_session()
        logger.debug(f"ASYNC Pool: {async_engine.pool.status()}")
        yield session
    except SQLAlchemyError as sql_ex:
        await session.rollback()
        raise sql_ex
    finally:
        await session.close()
