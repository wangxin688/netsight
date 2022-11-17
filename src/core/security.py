"""jwt auth token generate:
1. header:
    alg: HSA256
    type: Bearer
2. payload:
    iss(issuer): 签发人
    exp(expiration time)
    sub(subject): 主题
    and(audience): 受众
    nbf(Not Before): 生效时间
    iat(Issued At): 签发时间
    jti(JWT ID): 编号
    可新增自定义，jwt默认是不加密的，不要放入敏感信息
3. signature:
    对1.2两部分数据签名，防止被篡改
    需要制定一个secret_key，不能泄露，然后使用header中制定的签名算法，按照
    `HMAXSHA256(base64UrlEncode(header)+"."+base64UrlEncode(payload), secret)`的共识签名
4. 优势：
    基于token的绘画管理，不依赖cookie,可以防止csrf,同时服务端不需要存储session,但由于其本身无状态，
    一旦签发就无法在有效期内废止(规避方式可以加入黑名单方式)
"""
import time

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.api.auth.schemas import AccessToken
from src.core.config import settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_EXPIRE_SECS = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.SECURITY_BCRYPT_ROUNDS,
)


class JWTTokenPayload(BaseModel):
    sub: str | int
    refresh: bool
    issued_at: int
    expires_at: int


def create_jwt_token(subject: str | int, exp_secs: int, refresh: bool):
    """Creates jwt access or refresh token for user.
    Args:
        subject: anything unique to user, id or email etc.
        exp_secs: expire time in seconds
        refresh: if True, this is refresh token
    """

    issued_at = int(time.time())
    expires_at = issued_at + exp_secs

    to_encode: dict[str, int | str | bool] = {
        "issued_at": issued_at,
        "expires_at": expires_at,
        "sub": subject,
        "refresh": refresh,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt, expires_at, issued_at


def generate_access_token_response(subject: str | int, expired_time: int | None = None):
    """Generate tokens and return AccessTokenResponse"""
    if not expired_time:
        expired_time = ACCESS_TOKEN_EXPIRE_SECS
    access_token, expires_at, issued_at = create_jwt_token(
        subject, expired_time, refresh=False
    )
    refresh_token, refresh_expires_at, refresh_issued_at = create_jwt_token(
        subject, expired_time, refresh=True
    )
    return AccessToken(
        token_type="Bearer",
        access_token=access_token,
        expires_at=expires_at,
        issued_at=issued_at,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_expires_at,
        refresh_token_issued_at=refresh_issued_at,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain and hashed password matches
    Applies passlib context based on bcrypt algorithm on plain password.
    It takes about 0.3s for default 12 rounds of SECURITY_BCRYPT_DEFAULT_ROUNDS.
    """
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Creates hash from password
    Applies passlib context based on bcrypt algorithm on plain password.
    It takes about 0.3s for default 12 rounds of SECURITY_BCRYPT_DEFAULT_ROUNDS.
    """
    return PWD_CONTEXT.hash(password)
