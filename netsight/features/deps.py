import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from netsight.core.config import settings
from netsight.core.database.session import async_session
from netsight.core.errors.exception_handlers import PermissionDenyError, TokenExpireError, TokenInvalidError
from netsight.features.admin.models import RolePermission, User
from netsight.features.admin.security import API_WHITE_LISTS, JWT_ALGORITHM, JwtTokenPayload
from netsight.features.admin.services import user_service
from netsight.features.consts import ReservedRoleSlug
from netsight.libs.redis.session import CacheNamespace, redis_client

logger = logging.getLogger(__name__)

token = HTTPBearer()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = async_session()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.exception("Database error: %s", e)  # noqa: TRY401
        await session.rollback()
    finally:
        await session.aclose()


async def auth(
    request: Request, session: AsyncSession = Depends(get_session), token: HTTPAuthorizationCredentials = Depends(token)
) -> User:
    if token.scheme != "Bearer":
        raise TokenInvalidError
    if not token:
        raise TokenInvalidError
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.DecodeError as e:
        raise TokenInvalidError from e
    token_data = JwtTokenPayload(**payload)
    if token_data.refresh:
        raise TokenInvalidError
    now = datetime.now(tz=UTC)
    if now < token_data.issued_at or now > token_data.expires_at:
        raise TokenExpireError
    user = await user_service.get_one_or_404(session, token_data.sub, selectinload(User.role))
    check_user_active(user.is_active)
    operation_id = request.scope["route"].operation_id
    if operation_id and not check_privileged_role(user.role.slug, operation_id):
        await check_role_permissions(user.role_id, session, operation_id)
    return user


async def sqladmin_auth(token: str) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.DecodeError as e:
        raise TokenInvalidError from e
    token_data = JwtTokenPayload(**payload)
    if token_data.refresh:
        raise TokenInvalidError
    now = datetime.now(tz=UTC)
    if now < token_data.issued_at or now > token_data.expires_at:
        raise TokenExpireError
    async with async_session() as session:
        user = await user_service.get_one_or_404(session, token_data.sub, selectinload(User.role))
        check_user_active(user.is_active)
        if user.role.slug == ReservedRoleSlug.ADMIN:
            return user
        raise PermissionDenyError


def check_user_active(is_active: bool) -> None:
    if not is_active:
        raise PermissionDenyError


def check_privileged_role(slug: str, operation_id: str) -> bool:
    if slug == ReservedRoleSlug.ADMIN:
        return True
    return operation_id in API_WHITE_LISTS


async def check_role_permissions(role_id: int, session: AsyncSession, operation_id: str) -> None:
    permissions: list[str] | None = await redis_client.get_cache(name=str(role_id), namespace=CacheNamespace.ROLE_CACHE)
    if not permissions:
        _permissions = (
            await session.scalars(select(RolePermission.permission_id).where(RolePermission.role_id == role_id))
        ).all()
        if not _permissions:
            raise PermissionDenyError
        permissions = [str(p) for p in _permissions]
        await redis_client.set_nx(name=str(role_id), value=permissions, namespace=CacheNamespace.ROLE_CACHE)
    if operation_id not in permissions:
        raise PermissionDenyError


SqlaSession = Annotated[AsyncSession, Depends(get_session)]
AuthUser = Annotated[User, Depends(auth)]
