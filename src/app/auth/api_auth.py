import time
from datetime import datetime
from typing import Optional

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth import schemas
from src.app.auth.models import User
from src.app.base import BaseResponse
from src.app.deps import get_locale, get_session
from src.core.config import settings
from src.core.security import (
    JWT_ALGORITHM,
    JWTTokenPayload,
    generate_access_token_response,
    get_password_hash,
    verify_password,
)
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_404, ERR_NUM_10003, ResponseMsg, error_404_409
from src.utils.exceptions import TokenInvalidForRefreshError
from src.utils.external.lark_api import LarkClient
from src.utils.i18n_loaders import _

router = APIRouter(route_class=AuditRoute)


# demo bg_task1 and exceptions show
def bg_task1():
    logger.info("receive bg task...")
    # a = 1 / 0
    # logger.info(a)


@router.post("/register", response_model=BaseResponse[int])
async def register_new_user(
    bg_task: BackgroundTasks,
    auth_user: schemas.AuthUserCreate,
    session: AsyncSession = Depends(get_session),
    locale=Depends(get_locale),
):
    result = await session.execute(select(User).where(User.email == auth_user.email))
    if result.scalars().first() is not None:
        return_info = error_404_409(
            ERR_NUM_404, locale, "user", "email", auth_user.email
        )
        return return_info
    user = User(
        username=auth_user.username,
        hashed_password=get_password_hash(auth_user.password),
        email=auth_user.email,
    )
    session.add(user)
    await session.commit()
    return_info = ResponseMsg(data=user.id, locale=locale)
    bg_task.add_task(bg_task1)
    return return_info


@router.post("/login", response_model=BaseResponse[schemas.AccessToken])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    locale=Depends(get_locale),
):
    user: User = (
        (await session.execute(select(User).where(User.email == form_data.username)))
        .scalars()
        .first()
    )
    if user is None:
        return_info = error_404_409(
            ERR_NUM_404, locale, "user", "username", form_data.username
        )
        return return_info
    if not verify_password(form_data.password, user.hashed_password):
        return_info = ResponseMsg(
            code=ERR_NUM_10003.code,
            data=None,
            message=_(ERR_NUM_10003.message, locale=locale),
        )
        return return_info
    token = generate_access_token_response(str(user.id))
    return_info = ResponseMsg(data=token, locale=locale)
    user.last_login = datetime.now()
    session.add(user)
    await session.commit()
    return return_info


@router.post("/refresh-token", response_model=BaseResponse[schemas.AccessToken])
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_session),
    locale=Depends(get_locale),
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

    user: User = (
        (await session.execute(select(User).where(User.id == token_data.sub)))
        .scalars()
        .first()
    )

    if user is None:
        return_info = error_404_409(ERR_NUM_404, locale, "user", "#id", token_data.sub)
        return return_info
    token = generate_access_token_response(str(user.id))
    return_info = ResponseMsg(data=token, locale=locale)
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
