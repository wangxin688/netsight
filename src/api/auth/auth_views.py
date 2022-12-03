import time
from datetime import datetime
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from src.api.auth import schemas
from src.api.auth.models import User
from src.api.base import BaseResponse
from src.api.deps import audit_with_data, get_current_user, get_session
from src.core.config import settings
from src.core.security import (
    JWT_ALGORITHM,
    JWTTokenPayload,
    generate_access_token_response,
    get_password_hash,
    verify_password,
)
from src.utils.error_code import ERR_NUM_0, ERR_NUM_10001, ERR_NUM_10002, ERR_NUM_10003
from src.utils.exceptions import TokenInvalidForRefreshError
from src.utils.external.lark_api import LarkClient
from src.utils.loggers import logger

router = APIRouter()


@router.get("/item", response_model=BaseResponse[int])
async def get_abc(a: int, b: int, audit=Depends(audit_with_data)):
    assert isinstance(a, int), "bad type"
    logger.info(f"receive: {a}, {b}")
    return {"code": 0, "data": a + b, "msg": "success"}


@router.get("/test", response_model=BaseResponse[int])
async def log_test(
    a: int,
    b: int,
    audit=Depends(audit_with_data),
    user: User = Depends(get_current_user),
):
    logger.info(f"receive {a} {b}")
    res = a / b
    return {"code": 0, "data": res, "msg": "success"}


@router.post("/register", response_model=BaseResponse[int])
async def register_new_user(
    auth_user: schemas.AuthUserCreate,
    session: AsyncSession = Depends(get_session),
):
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
    return return_info


@router.post("/login", response_model=BaseResponse[schemas.AccessToken])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result: AsyncResult = await session.execute(
        select(User).where(User.email == form_data.username)
    )
    user: User | None = result.scalars().first()
    if not user:
        return ERR_NUM_10002.dict()
    if not verify_password(form_data.password, user.hashed_password):
        return ERR_NUM_10003.dict()
    return_info = ERR_NUM_0.dict()
    token = generate_access_token_response(str(user.id))
    return_info["data"] = token
    user.updated_at = datetime.now()
    session.add(user)
    await session.commit()
    return return_info


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
