import re
import time
from typing import AsyncGenerator

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.models import User

# from src.api.auth.plugins import auth_plugins
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

# oauth2_scheme = auth_plugins(settings.AUTH)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/jwt/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def audit_with_data(audit: bool = True) -> bool:
    return audit


def audit_without_data(audit: bool = True) -> bool:
    return audit


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
    if user._has_roles(["superuser"]):
        return user
    path = request.url.path
    request.method
    # TODO: confirm blacklist and whitelist? define all in database or not?
    # TODO: more flexible rbac? role to api path permission and group to specific department or device_role or site?
    # if user._has_roles(["admin"]):
    #     if path in ADMIN_INVALID_URLS:
    #         raise PermissionError
    #     return user
    # for valid_url in USER_VALID_URLS:
    #     if re.match(valid_url, path):
    #         return user
    permission_dict: dict = request.state.permissions
    for item in permission_dict.values():
        urls = item["urls"]
        for reg in urls:
            reg = "^%s$" % reg
            if re.match(reg, path):
                return user
    raise PermissionDenyError


# class RBACChecker:
#     def __init__(
#         self,
#         roles: str | Sequence[str] = None,
#         groups: str | Sequence[str] = None,
#         permissions: str | Sequence[str] = None,
#     ) -> None:
#         self.roles = roles
#         self.groups = groups
#         self.permissions = permissions

#     async def __call__(
#         self,
#         request: Request,
#         user: User = Depends(get_current_user),
#         session: AsyncSession = Depends(get_session),
#     ):
