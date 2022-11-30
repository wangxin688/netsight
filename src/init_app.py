import asyncio

from src.api.auth.models import Role, User
from src.core.config import settings
from src.core.security import get_password_hash
from src.db.db_session import async_session


async def init_app():
    async with async_session() as session:
        superuser_role = Role(name="superuser", description="super admin of system")
        session.add(superuser_role)
        await session.commit()
        await session.flush()
        superuser = User(
            username=settings.FIRST_SUPERUSER_NAME,
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role_id=superuser_role.id,
        )
        session.add(superuser)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_app())
