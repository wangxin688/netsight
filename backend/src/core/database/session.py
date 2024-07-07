import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import _Env, settings

logger = logging.getLogger(__name__)

if _Env.PROD.name == settings.ENV:
    async_engine = create_async_engine(
        url=settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        future=True,
        pool_size=settings.DATABASE_POOL_SIZE,
        connect_args={"server_settings": {"jit": "off"}},
        max_overflow=settings.DATABASE_POOL_MAX_OVERFLOW,
    )
else:
    # compatibility with pytest
    async_engine = create_async_engine(
        url=settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, future=True, poolclass=NullPool
    )
async_session = async_sessionmaker(async_engine, autoflush=False, expire_on_commit=False)
