import time
from typing import AsyncGenerator, Sequence

import jwt
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.models import User
from src.api.auth.plugins import auth_plugins
from src.core import security
from src.core.config import settings
from src.db.db_session import async_session
from src.utils.exceptions import (
    PermissionDenyError,
    TokenExpiredError,
    TokenInvalidError,
    TokenInvalidForRefreshError,
    UserNotFoundError,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: str = Depends(auth_plugins[settings.AUTH]),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.JWT_ALGORITHM]
        )
    except jwt.DecodeError:
        raise TokenInvalidError
    # JWT guarantees payload will be unchanged (and thus valid), no errors here
    token_data = security.JWTTokenPayload(**payload)

    if token_data.refresh:
        raise TokenInvalidForRefreshError
    now = int(time.time())
    if now < token_data.issued_at or now > token_data.expires_at:
        raise TokenExpiredError
    result = await session.execute(select(User).where(User.id == int(token_data.sub)))
    user: User | None = result.scalars().first()

    if not user:
        raise UserNotFoundError
    request.state.current_user = user.email
    return user


class RBACChecker:
    def __init__(
        self,
        roles: str | Sequence[str] = None,
        groups: str | Sequence[str] = None,
        permissions: str | Sequence[str] = None,
    ) -> None:
        self.roles = roles
        self.groups = groups
        self.permissions = permissions

    async def __call__(
        self,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ):
        result = await user.has_requires(
            session, roles=self.roles, groups=self.groups, permissions=self.permissions
        )
        if not result:
            raise PermissionDenyError
        return user
