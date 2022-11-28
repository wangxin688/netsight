import time
from typing import AsyncGenerator, NamedTuple, Optional

import jwt
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.constrants import USER_WHITE_LIST
from src.api.auth.models import User
from src.api.auth.plugins import auth_plugins
from src.api.auth.services import url_match
from src.core import security
from src.core.config import settings
from src.db.db_session import async_session
from src.utils.exceptions import (
    PermissionDenyError,
    ResourceNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TokenInvalidForRefreshError,
)

oauth2_scheme = auth_plugins(settings.AUTH)


class CommonParams(NamedTuple):
    limit: int
    offset: int
    q: Optional[str]


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def audit_with_data(audit: bool = True) -> bool:
    return audit


def audit_without_data(audit: bool = True) -> bool:
    return audit


def common_params(limit: int = 20, offset: int = 0, q: str = None):
    result = CommonParams(limit, offset, q)
    return result


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
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
        raise ResourceNotFoundError
    request.state.current_user = user

    path = request.url.path
    method = request.method
    if url_match(path, method, USER_WHITE_LIST):
        return user
    user_role = user.role
    if user.role == "superuser":
        return user
    if user_role == "admin":
        if url_match(path, method, USER_WHITE_LIST):
            return user
    permissions = request.state.permissions.get(user_role)
    if permissions is None:
        return user
    if url_match(path, method, permissions):
        return user
    raise PermissionDenyError
