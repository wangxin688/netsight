import time
from typing import AsyncGenerator, Literal

import jwt
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.auth.const import USER_WHITE_LIST
from src.app.auth.models import User
from src.app.auth.plugins import auth_plugins
from src.app.auth.services import url_match
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


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def audit_with_data(audit: bool = True) -> bool:
    return audit


def audit_without_data(audit: bool = True) -> bool:
    return audit


def get_locale(
    request: Request,
) -> Literal["en_US", "zh_CN"]:
    return request.headers.get("Accept-Language", "en_US")


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
    user: User = (
        (
            await session.execute(
                select(User)
                .where(User.id == int(token_data.sub))
                .options(selectinload(User.auth_role))
            )
        )
        .scalars()
        .first()
    )

    if not user:
        raise ResourceNotFoundError
    request.state.current_user = user
    path = request.url.path
    method = request.method
    if url_match(path, method, USER_WHITE_LIST):
        return user
    user_role = user.auth_role.name
    if user_role == "superuser":
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
