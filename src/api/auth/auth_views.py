import time
from datetime import datetime
from typing import Optional

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from src.api.auth import schemas
from src.api.auth.models import User
from src.api.base import BaseResponse
from src.api.deps import get_session
from src.core.config import settings
from src.core.security import (
    JWT_ALGORITHM,
    JWTTokenPayload,
    generate_access_token_response,
    get_password_hash,
    verify_password,
)
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_0, ERR_NUM_10001, ERR_NUM_10002, ERR_NUM_10003
from src.utils.exceptions import TokenInvalidForRefreshError
from src.utils.external.lark_api import LarkClient

router = APIRouter(route_class=AuditRoute)


# demo bg_task1 and exceptions show
def bg_task1():
    logger.info("recive bg task...")
    # a = 1 / 0
    # logger.info(a)


@router.post("/register", response_model=BaseResponse[int])
async def register_new_user(
    bg_task: BackgroundTasks,
    auth_user: schemas.AuthUserCreate,
    session: AsyncSession = Depends(get_session),
):
    logger.info("recived new_role")
    result = await session.execute(select(User).where(User.email == auth_user.email))
    if result.scalars().first() is not None:
        return ERR_NUM_10001
    user = User(
        username=auth_user.username,
        hashed_password=get_password_hash(auth_user.password),
        email=auth_user.email,
    )
    session.add(user)
    await session.commit()
    return_info = ERR_NUM_0
    return_info.data = user.id
    bg_task.add_task(bg_task1)
    return return_info.dict()


@router.post("/login", response_model=BaseResponse[schemas.AccessToken])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    logger.info("Login start")
    result: AsyncResult = await session.execute(
        select(User).where(User.email == form_data.username)
    )
    user: User | None = result.scalars().first()
    if not user:
        return ERR_NUM_10002.dict()
    if not verify_password(form_data.password, user.hashed_password):
        return ERR_NUM_10003.dict()
    return_info = ERR_NUM_0
    token = generate_access_token_response(str(user.id))
    return_info.data = token
    user.updated_at = datetime.now()
    session.add(user)
    await session.commit()
    return return_info.dict()


@router.post("/refresh-token", response_model=BaseResponse[schemas.AccessToken])
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_session),
):
    """OAuth2 compatible token, get an access token for future requests using refresh token"""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except (jwt.DecodeError, RequestValidationError):
        raise TokenInvalidForRefreshError

    # JWT guarantees payload will be unchanged (and thus valid), no errors here
    token_data = JWTTokenPayload(**payload)

    if not token_data.refresh:
        raise TokenInvalidForRefreshError
    now = int(time.time())
    if now < token_data.issued_at or now > token_data.expires_at:
        raise TokenInvalidForRefreshError

    result: AsyncResult = await session.execute(
        select(User).where(User.id == token_data.sub)
    )
    user: User | None = result.scalars().first()

    if user is None:
        return ERR_NUM_10001.dict()

    token = generate_access_token_response(str(user.id))
    return_info = ERR_NUM_0.dict()
    return_info["data"] = token
    return return_info


@router.post("/lark-login")
async def lark_login(
    code: str,
    user_agent: Optional[str],
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    app_access_token = request.state.app_access_token
    lark_api = LarkClient(token=app_access_token)
    await lark_api.get_user_identity(code)
    # TODO: complete the oauth2 code bearer process
