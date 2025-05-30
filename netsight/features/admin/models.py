from datetime import datetime
from typing import ClassVar
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, and_, func, select
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, backref, column_property, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from netsight.core.database import Base
from netsight.core.database.mixins import AuditTimeMixin
from netsight.core.database.types import bool_false, bool_true, int_pk, uuid_pk

__all__ = ("RolePermission", "RoleMenu", "Role", "Permission", "Group", "User", "Menu")


class RolePermission(Base):
    __tablename__ = "role_permission"
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"), primary_key=True)


class RoleMenu(Base):
    __tablename__ = "role_menu"
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    menu_id: Mapped[UUID] = mapped_column(ForeignKey("menu.id"), primary_key=True)


class User(Base, AuditTimeMixin):
    __tablename__ = "user"
    __search_fields__: ClassVar = {"email", "name"}
    __visible_name__ = {"en": "User", "zh": "用户"}
    id: Mapped[int_pk]
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    avatar: Mapped[str | None]
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool_true]
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id", ondelete="CASCADE"))
    group: Mapped["Group"] = relationship(back_populates="user", passive_deletes=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="CASCADE"))
    role: Mapped["Role"] = relationship(backref="user", passive_deletes=True)
    auth_info: Mapped[dict | None] = mapped_column(MutableDict.as_mutable(JSON))


class Group(Base, AuditTimeMixin):
    __tablename__ = "group"
    __search_fields__: ClassVar = {"name"}
    __visible_name__ = {"en": "Group", "zh": "用户组"}
    id: Mapped[int_pk] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None]
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="CASCADE"))
    role: Mapped["Role"] = relationship(backref="group", passive_deletes=True)
    user: Mapped[list["User"]] = relationship(back_populates="group")
    user_count: Mapped[int] = column_property(
        select(func.count(User.id)).where(User.group_id == id).scalar_subquery(),
        deferred=True,
    )


class Permission(Base):
    __tablename__ = "permission"
    __visible_name__ = {"en": "Permission", "zh": "权限"}
    id: Mapped[uuid_pk]
    name: Mapped[str]
    url: Mapped[str]
    method: Mapped[str]
    tag: Mapped[str]
    role: Mapped[list["Role"]] = relationship(secondary="role_permission", back_populates="permission")


class Role(Base, AuditTimeMixin):
    __tablename__ = "role"
    __search_fields__: ClassVar = {"name"}
    __visible_name__ = {"en": "Role", "zh": "用户角色"}
    id: Mapped[int_pk] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None]
    permission: Mapped[list["Permission"]] = relationship(secondary="role_permission", back_populates="role")
    menu: Mapped[list["Menu"]] = relationship(secondary="role_menu", back_populates="role")

    permission_count: Mapped[int] = column_property(
        select(func.count(Permission.id))
        .where(and_(RolePermission.role_id == id, RolePermission.permission_id == Permission.id))
        .scalar_subquery(),
        deferred=True,
    )
    user_count: Mapped[int] = column_property(
        select(func.count(User.id)).where(User.role_id == id).scalar_subquery(),
        deferred=True,
    )


class Menu(Base):
    __tablename__ = "menu"
    __visible_name__ = {"en": "Menu", "zh": "菜单"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, comment="the unique name of route")
    hidden: Mapped[bool_false]
    redirect: Mapped[str] = mapped_column(comment="redirect url for the route")
    hideChildrenInMenu: Mapped[bool_false] = mapped_column(comment="hide children in menu force or not")  # noqa: N815
    order: Mapped[int]
    title: Mapped[str] = mapped_column(comment="the title of the route, 面包屑")
    icon: Mapped[str | None]
    keepAlive: Mapped[bool_false] = mapped_column(comment="cache route, 开启multi-tab时为true")  # noqa: N815
    hiddenHeaderContent: Mapped[bool_false] = mapped_column(comment="隐藏pageheader页面带的面包屑和标题栏")  # noqa: N815
    permission: Mapped[list[int] | None] = mapped_column(ARRAY(Integer, dimensions=1))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey(id, ondelete="CASCADE"))
    children: Mapped[list["Menu"]] = relationship(
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )
    role: Mapped[list["Role"]] = relationship(back_populates="menu", secondary="role_menu")
