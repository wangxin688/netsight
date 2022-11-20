from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import NullPool

from src.core.config import settings

async_sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(
    async_sqlalchemy_database_uri, pool_pre_ping=True, poolclass=NullPool
)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
