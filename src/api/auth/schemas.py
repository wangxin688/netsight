from pydantic import EmailStr

from src.api.base import BaseModel


class AccessToken(BaseModel):
    token_type: str
    access_token: str
    expires_at: int
    issued_at: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int


class User(BaseModel):
    username: str
    email: EmailStr
    avatar: str
    is_active: bool
    role: str
