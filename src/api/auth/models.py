from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import TimestampMixin

__all__ = (
    "User",
    "UserGroupLink",
    "RolePermissionLink",
    "Group",
    "Permission",
    "Role",
)

CONFIG = "english"


class UserGroupLink(Base):
    """user to group many-to-many relationship"""

    __tablename__ = "auth_user_group_link"
    user_id = Column(Integer, ForeignKey("auth_user.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("auth_group.id"), primary_key=True)


class RolePermissionLink(Base):
    """role to permission many-to-many relationship"""

    __tablename__ = "auth_role_permission_link"
    role_id = Column(Integer, ForeignKey("auth_role.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("auth_permission.id"), primary_key=True)


class User(Base, TimestampMixin):
    """auth user table"""

    __tablename__ = "auth_user"
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, server_default=expression.true(), nullable=False)
    role_id = Column(
        Integer, ForeignKey("auth_role.id", ondelete="SET NULL"), nullable=True
    )
    auth_role = relationship("Role", back_populates="auth_user", overlaps="auth_user")
    auth_group = relationship(
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
        return self.auth_role[0].name


class Group(Base):
    """auth user group table"""

    __tablename__ = "auth_group"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    auth_user = relationship(
        "User",
        secondary="auth_user_group_link",
        back_populates="auth_group",
        overlaps="auth_group",
    )


class Role(Base):
    __tablename__ = "auth_role"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    auth_user = relationship("User", back_populates="auth_role", passive_deletes=True)
    auth_permission = relationship(
        "Permission",
        secondary="auth_role_permission_link",
        back_populates="auth_role",
        overlaps="auth_role",
        lazy="joined",
    )


class Permission(Base):
    __tablename__ = "auth_permission"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=False)
    action = Column(
        ENUM("GET", "PUT", "POST", "DELETE", name="method", create_type=False),
        nullable=False,
    )
    auth_role = relationship(
        "Role",
        secondary="auth_role_permission_link",
        back_populates="auth_permission",
        overlaps="auth_permission",
    )
