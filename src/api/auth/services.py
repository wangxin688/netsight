import asyncio
import functools
import inspect
import time
import typing

import jwt
from fastapi import Depends, FastAPI, WebSocket, params
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware

from src.api.auth.models import User
from src.api.deps import oauth2_scheme
from src.core import security
from src.core.config import settings
from src.utils.exceptions import (
    ResourceNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TokenInvalidForRefreshError,
)


class AuthBackend(AuthenticationBackend, User):
    def __init__(self, auth: "Auth") -> None:
        self.auth = auth

    @staticmethod
    def get_user_token(request: Request) -> typing.Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        return None if not authorization or scheme.lower() != "bearer" else token

    async def authenticate(
        self, request: Request
    ) -> typing.Optional[typing.Tuple["Auth", typing.Optional[User]]]:
        return self.auth, await self.auth.get_current_user(request)

    def attach_middleware(self, app: FastAPI):
        app.add_middleware(AuthenticationMiddleware, backend=self)


class Auth(User):
    user_model: User = None
    session: AsyncSession = None
    backend: AuthBackend[User] = None

    def __init__(
        self,
        session: AsyncSession,
        user_model=User,
        pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto"),
    ) -> None:
        self.user_model = user_model or self.user_model
        assert self.user_model, "user_model is not defined"
        self.session = session or self.session
        self.backend = self.backend or AuthBackend(self)
        self.pwd_context = pwd_context

    async def auth_user(
        self, email: str, password: typing.Union[str, SecretStr]
    ) -> typing.Optional[User]:
        result: AsyncResult = await self.session.execute(
            select(self.user_model).where(self.user_model.email == email)
        )
        user: User | None = result.scalars().first()
        if user:
            pwd = (
                password.get_secret_value()
                if isinstance(password, SecretStr)
                else password
            )
            pwd2 = (
                user.password.get_secret_value()
                if isinstance(user.password, SecretStr)
                else user.password
            )
            if self.pwd_context.verify(pwd, pwd2):  # 用户存在 且 密码验证通过
                return user
        return None

    def get_current_user(self):
        async def _get_current_user(
            request: Request, token=Depends(oauth2_scheme)
        ) -> typing.Optional[User]:
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
            result = await self.session.execute(
                select(User).where(User.id == int(token_data.sub))
            )
            user: User | None = result.scalars().first()

            if not user:
                raise ResourceNotFoundError
            request.state.current_user = user.email
            return request.user

        return _get_current_user

    def requires(
        self,
        roles: str | typing.Sequence[str] = None,
        groups: str | typing.Sequence[str] = None,
        permissions: str | typing.Sequence[str] = None,
        status_code: int = 200,
        redirect: str = None,
        response: bool | Response = None,
    ) -> typing.Callable:
        (groups,) if not groups or isinstance(groups, str) else tuple(groups)
        (roles,) if not roles or isinstance(roles, str) else tuple(roles)
        (permissions,) if not permissions or isinstance(permissions, str) else tuple(
            permissions
        )

        async def has_requires(user: User) -> bool:
            return (
                user
                and (
                    await self.session.execute(
                        select(
                            user.has_requires,
                            roles=roles,
                            groups=groups,
                            permissions=permissions,
                        )
                    )
                )
                .scalars()
                .first()
            )

        async def depend(
            request: Request, user: User = Depends(self.get_current_user)
        ) -> bool | Response:
            user_auth = request.scope.get("__user_auth__", None)
            if user_auth is None:
                request.scope["__user_auth__"] = {}
            if isinstance(user, params.Depends):
                user = await self.get_current_user(request)
            await has_requires(user)
            if response is not None:
                return response
            # code, headers = status_code, {}

        def decorator(
            func: typing.Callable = None,
        ) -> typing.Callable | typing.Coroutine:
            if func is None:
                return depend
            if isinstance(func, Request):
                return depend(func)
            sig = inspect.signature(func)
            for idx, parameter in enumerate(sig.parameters.values()):  # noqa: B007
                if parameter.name in ["request", "websocket"]:
                    type_ = parameter.name
                    break
            else:
                raise Exception(
                    f'No "request" or "websocket" argument on function "{func}"'
                )
            if type_ == "websocket":
                # Handle websocket functions. (Always async)
                @functools.wraps(func)
                async def websocket_wrapper(
                    *args: typing.Any, **kwargs: typing.Any
                ) -> None:
                    websocket = kwargs.get("websocket", args[idx] if args else None)
                    assert isinstance(websocket, WebSocket)
                    user = await self.get_current_user(websocket)  # type: ignore
                    if not await has_requires(user):
                        await websocket.close()
                    else:
                        await func(*args, **kwargs)

                return websocket_wrapper

            elif asyncio.iscoroutinefunction(func):
                # Handle async request/response functions.
                @functools.wraps(func)
                async def async_wrapper(
                    *args: typing.Any, **kwargs: typing.Any
                ) -> Response:
                    request = kwargs.get("request", args[idx] if args else None)
                    assert isinstance(request, Request)
                    response = await depend(request)
                    if response is True:
                        return await func(*args, **kwargs)
                    return response

                return async_wrapper

            else:
                # Handle sync request/response functions.
                @functools.wraps(func)
                def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
                    request = kwargs.get("request", args[idx] if args else None)
                    assert isinstance(request, Request)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        loop.create_task(depend(request))
                    )
                    if response is True:
                        return func(*args, **kwargs)
                    return response

                return sync_wrapper

        return decorator
