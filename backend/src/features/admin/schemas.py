from datetime import datetime
from uuid import UUID

from src.features._types import AuditTime, BaseModel, QueryParams


class AccessToken(BaseModel):
    token_type: str = "Bearer"
    access_token: str
    expires_at: datetime
    issued_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
    refresh_token_issued_at: datetime


class Permission(BaseModel):
    id: UUID
    name: str
    url: str
    method: str
    tag: str


class PermissionCreate(BaseModel): ...


class PermissionUpdate(BaseModel): ...


class PermissionQuery(QueryParams): ...


class UserBase(BaseModel):
    name: str
    email: str | None = None
    avatar: str | None = None


class UserBrief(UserBase):
    id: int


class GroupBase(BaseModel):
    name: str
    description: str | None = None


class GroupBrief(BaseModel):
    id: int
    name: str


class RoleBase(BaseModel):
    name: str
    slug: str
    description: str


class RoleBrief(BaseModel):
    id: int
    name: str


class MenuBase(BaseModel):
    name: str
    hidden: bool
    redirect: str
    hideChildrenInMenu: bool
    order: int
    title: str
    icon: str | None = None
    keepAlive: bool
    hiddenHeaderContent: bool
    permission: list[int]
    parent_id: int


class MenuCreate(MenuBase):
    id: int


class MenuMeta(BaseModel):
    title: str
    icon: str
    hidden: bool
    keepAlive: bool
    hiddenHeaderContent: bool
    permission: list[int]
    hideChildrenInMenu: bool


class MenuTree(BaseModel):
    id: int
    name: str
    redirect: str
    meta: MenuMeta
    children: list["MenuTree"]


class MenuUpdate(BaseModel):
    name: str | None = None
    hidden: bool | None = None
    redirect: str | None = None
    hideChildrenInMenu: bool | None = None
    order: int | None = None
    title: str | None = None
    icon: str | None = None
    keepAlive: bool | None = None
    hiddenHeaderContent: bool | None = None
    permission: list[int] | None = None
    parent_id: int | None = None


class MenuQuery(QueryParams): ...


class UserCreate(UserBase):
    group_id: int
    role_id: int | None = None


class GroupCreate(GroupBase):
    password: str
    role_id: int
    user: list[int]


class RoleCreate(RoleBase):
    permission: list[int]


class UserUpdate(UserCreate):
    name: str | None = None
    password: str | None = None
    group_id: int | None = None


class GroupUpdate(GroupCreate):
    name: str | None = None
    role_id: int | None = None


class RoleUpdate(RoleCreate):
    name: str | None = None
    description: str | None = None


class User(UserBase, AuditTime):
    id: int
    role: RoleBrief
    group: GroupBrief


class Group(GroupBase, AuditTime):
    id: int
    user_count: int
    role: RoleBrief


class Role(RoleBase, AuditTime):
    id: int
    permission: list[Permission]
    user_count: int


class RoleList(RoleBase, AuditTime):
    id: int
    permission_count: int


class UserQuery(QueryParams): ...


class GroupQuery(QueryParams): ...


class RoleQuery(QueryParams): ...
