from datetime import datetime
from typing import List, Literal, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import TimestampMixin

__all__ = ("User", "UserGroupLink", "RolePermissionLink", "Group", "Permission", "Role")

CONFIG = "english"


class UserGroupLink(Base):
    """user to group many-to-many relationship"""

    __tablename__ = "auth_user_group_link"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_user.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_group.id"), primary_key=True)


class RolePermissionLink(Base):
    """role to permission many-to-many relationship"""

    __tablename__ = "auth_role_permission_link"
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_role.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_permission.id"), primary_key=True)


class User(Base, TimestampMixin):
    """auth user table"""

    __tablename__ = "auth_user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=expression.true(), nullable=False)
    role_id: Mapped[Optional[str]] = mapped_column(
        Integer, ForeignKey("auth_role.id", ondelete="SET NULL"), nullable=True
    )
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    auth_role: Mapped["Role"] = relationship("Role", back_populates="auth_user", overlaps="auth_user")
    auth_group: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="auth_user_group_link",
        back_populates="auth_user",
        overlaps="auth_user",
    )

    @property
    def is_authenticated(self) -> bool:
        return self.is_active

    @property
    def identity(self) -> str:
        return self.username.title()

    @property
    def role(self) -> str:
        return self.auth_role.name


class Group(Base):
    """auth user group table"""

    __tablename__ = "auth_group"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    auth_user: Mapped[List[User]] = relationship(
        "User", secondary="auth_user_group_link", back_populates="auth_group", overlaps="auth_group"
    )


class Role(Base):
    __tablename__ = "auth_role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    auth_user: Mapped[List[User]] = relationship("User", back_populates="auth_role", passive_deletes=True)
    auth_permission: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="auth_role_permission_link",
        back_populates="auth_role",
        overlaps="auth_role",
        lazy="joined",
    )


class Permission(Base):
    __tablename__ = "auth_permission"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[Literal["GET", "PUT", "POST", "DELETE"]] = mapped_column(
        ENUM("GET", "PUT", "POST", "DELETE", name="method", create_type=False), nullable=False
    )
    auth_role: Mapped[List["Role"]] = relationship(
        "Role", secondary="auth_role_permission_link", back_populates="auth_permission", overlaps="auth_permission"
    )
