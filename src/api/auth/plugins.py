from typing import Dict, Literal, Optional

from fastapi import Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from src.core.config import settings
from src.utils.exceptions import TokenInvalidExpiredError


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
                raise TokenInvalidExpiredError
            else:
                return None  # pragma: nocover
        return param


def auth_plugins(plugins: Literal["Lark", "AD", "Simple"] = "Simple"):
    lark_oauth2_schema = CustomOAuth2AuthorizationCodeBearer(
        authorizationUrl=settings.REDIRECT_URI,
        tokenUrl="auth/login",
        refreshUrl="auth/refresh-token",
    )
    password_oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/access-token")
    auth_choices = {"Simple": password_oauth2_schema, "Lark": lark_oauth2_schema}
    return auth_choices[plugins]
