from datetime import datetime
from typing import List, Literal, Optional

from pydantic import EmailStr, validator

from src.api.base import BaseModel, BaseQuery
from src.utils.validators import items_to_list


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
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AuthUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
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


class AuthGroupBase(BaseModel):
    id: int
    name: str
    description: str | None

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
    auth_group_ids: int | List[int] | None

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v

    @validator("auth_group_ids")
    def auth_user_id_trans(cls, v):
        v = items_to_list(v)
        return v


class AuthUserQuery(BaseQuery):
    ids: List[int] | None
    name: List[str] | None


class AuthUserBulkDelete(BaseModel):
    ids: List[int]


class AuthGroupCreate(BaseModel):
    name: str
    description: str | None
    auth_user_ids: int | List[int] | None

    @validator("auth_user_ids")
    def auth_user_id_trans(cls, v):
        v = items_to_list(v)
        return v


class AuthGroupUpdate(BaseModel):
    name: str | None
    description: str | None
    auth_user_ids: int | List[int] | None

    @validator("auth_user_ids")
    def auth_user_id_trans(cls, v):
        v = items_to_list(v)
        return v


class AuthGroupQuery(BaseQuery):
    ids: List[int] | None
    name: List[str] | None


class AuthRoleCreate(BaseModel):
    name: str
    description: str | None
    auth_permission_ids: int | List[int] | None

    @validator("auth_permission_ids")
    def id_trans(cls, v):
        v = items_to_list(v)
        return v


class AuthRoleUpdate(BaseModel):
    name: str | None
    description: str | None
    auth_permission_ids: int | List[int] | None

    @validator("auth_permission_ids")
    def id_trans(cls, v):
        v = items_to_list(v)
        return v


class AuthRoleQuery(BaseQuery):
    ids: List[int] | None
    name: List[str] | None


class AuthRoleBulkDelete(BaseModel):
    ids: List[int]


class AuthPermissionCreate(BaseModel):
    name: str
    url: str
    action: Literal["GET", "PUT", "POST", "DELETE"]
    auth_role_ids: int | List[int] | None


class AuthPermissionUpdate(BaseModel):
    name: str | None
    url: str | None
    action: Literal["GET", "PUT", "POST", "DELETE"]
    auth_role_ids: int | List[int] | None


class AuthPermissionQuery(BaseQuery):
    ids: List[int] | None
