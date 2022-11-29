from typing import Dict, Literal, Optional

from fastapi import Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from src.core.config import settings
from src.utils.exceptions import TokenInvalidError


class CustomOAuth2PasswordBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise TokenInvalidError
            else:
                return None
        return param


class CustomOAuth2AuthorizationCodeBearer(OAuth2):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        refreshUrl: Optional[str] = None,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            authorizationCode={
                "authorizationUrl": authorizationUrl,
                "tokenUrl": tokenUrl,
                "refreshUrl": refreshUrl,
                "scopes": scopes,
            }
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise TokenInvalidError
            else:
                return None  # pragma: nocover
        return param


def auth_plugins(plugins: Literal["Lark", "Simple"] = "Simple"):
    auth_choices = {}
    if plugins == "Lark":
        lark_oauth2_schema = CustomOAuth2AuthorizationCodeBearer(
            authorizationUrl=settings.REDIRECT_URI,
            tokenUrl="auth/lark-login",
            refreshUrl="auth/refresh-token",
        )
        auth_choices.update({"Lark": lark_oauth2_schema})
    if plugins == "Simple":
        password_oauth2_schema = CustomOAuth2PasswordBearer(tokenUrl="auth/login")
        auth_choices.update({"Simple": password_oauth2_schema})
    return auth_choices[plugins]
