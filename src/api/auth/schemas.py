from typing import List, Optional

from pydantic import EmailStr, Field, validator

from src.api.base import BaseModel


class AccessToken(BaseModel):
    token_type: str
    access_token: str
    expires_at: int
    issued_at: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int


class AuthPermission(BaseModel):
    id: int
    name: str
    url: str | None
    action: str

    class Config:
        orm_mode = True


class AuthRole(BaseModel):
    id: int
    name: str
    description: str | None
    auth_permission: Optional[List[AuthPermission]]

    class Config:
        orm_mode = True


class AuthRoleBase(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


class AuthUserBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None
    is_active: bool

    class Config:
        orm_mode = True


class AuthUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None
    is_active: bool
    auth_role: Optional[AuthRole]

    class Config:
        orm_mode = True


class AuthGroup(BaseModel):
    id: int
    name: str
    description: str | None
    auth_user: Optional[List[AuthUserBase]]

    class Config:
        orm_mode = True


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


class AuthUserUpdate(BaseModel):
    username: str | None
    email: EmailStr | None
    password: str | None
    password2: str | None

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


class AuthUserQuery(BaseModel):
    id: Optional[List[int]] = Field(description="list auth user ids", ge=1)
