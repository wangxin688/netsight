from pydantic import EmailStr, validator

from src.api.base import BaseModel


class AccessToken(BaseModel):
    token_type: str
    access_token: str
    expires_at: int
    issued_at: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int


class AuthUser(BaseModel):
    username: str
    email: EmailStr
    avatar: str
    is_active: bool
    role: str


class AuthUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    password2: str

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


class AuthUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
