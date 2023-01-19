from typing import TYPE_CHECKING, AsyncGenerator

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from src.core.config import settings

async_sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(
    async_sqlalchemy_database_uri,
    pool_pre_ping=True,
    future=True,
)
async_session = sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)  # type: ignore

if TYPE_CHECKING:
    async_session: sessionmaker[AsyncSession]  # type: ignore


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        session: AsyncSession = async_session()
        logger.debug(f"ASYNC Pool: {async_engine.pool.status()}")
        yield session
    except SQLAlchemyError as sql_ex:
        await session.rollback()
        raise sql_ex
    finally:
        await session.close()
