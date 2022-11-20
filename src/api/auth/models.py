import typing

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.selectable import Exists

from src.db.db_base import Base
from src.db.db_mixin import TimestampMixin

__all__ = (
    "User",
    "UserRoleLink",
    "UserGroupLink",
    "GroupRoleLink",
    "RolePermissionLink",
    "Group",
    "Permission",
    "Role",
)

CONFIG = "english"


class UserRoleLink(Base):
    """user to role many-to-many relationship"""

    __tablename__ = "auth_user_roles"
    user_id = Column(Integer, ForeignKey("auth_user.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("auth_role.id"), primary_key=True)


class UserGroupLink(Base):
    """user to group many-to-many relationship"""

    __tablename__ = "auth_user_groups"
    user_id = Column(Integer, ForeignKey("auth_user.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("auth_group.id"), primary_key=True)


class GroupRoleLink(Base):
    """group to role many-to-many relationship"""

    __tablename__ = "auth_group_roles"
    group_id = Column(Integer, ForeignKey("auth_group.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("auth_role.id"), primary_key=True)


class RolePermissionLink(Base):
    """role to permission many-to-many relationship"""

    __tablename__ = "auth_role_permissions"
    role_id = Column(Integer, ForeignKey("auth_role.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("auth_permission.id"), primary_key=True)


class User(Base, TimestampMixin):
    """auth user table"""

    __tablename__ = "auth_user"
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, default=True)
    groups = relationship(
        "Group", secondary="auth_user_groups", back_populates="users", overlaps="users"
    )
    roles = relationship(
        "Role", secondary="auth_user_roles", back_populates="users", overlaps="users"
    )

    @property
    def is_authenticated(self) -> bool:
        return self.is_active

    @property
    def identity(self) -> str:
        return self.username.title()

    def _has_role(self, *role_where_clause: typing.Any) -> Exists:
        # add user.roles ?
        user_role_ids = (
            select(Role.id)
            .join(
                UserRoleLink,
                (UserRoleLink.user_id == self.id) & (UserRoleLink.role_id == Role.id),
            )
            .where(*role_where_clause)
        )
        role_group_ids = select(GroupRoleLink.group_id).join(
            Role, and_(*role_where_clause, Role.id == GroupRoleLink.role_id)
        )
        group_user_ids = (
            select(UserGroupLink.user_id)
            .where(UserGroupLink.user_id == self.id)
            .where(UserGroupLink.group_id.in_(role_group_ids))
        )
        return user_role_ids.exists() | group_user_ids.exists()

    def _has_roles(self, roles: typing.List[str]) -> Exists:

        return self._has_role(Role.slug.in_(roles))

    def _has_groups(self, groups: typing.List[str]) -> Exists:
        group_ids = (
            select(Group.id)
            .join(
                UserRoleLink,
                (UserGroupLink.user_id == self.id)
                & (UserGroupLink.group_id == Group.id),
            )
            .where(Group.slug.in_(groups))
        )
        return group_ids.exists()

    def _has_permissions(self, permissions: typing.List[str]) -> Exists:
        role_ids = select(RolePermissionLink.role_id).join(
            Permission,
            Permission.slug.in_(permissions)
            & (Permission.id == RolePermissionLink.permission_id),
        )
        return self._has_role(Role.id.in_(role_ids))

    async def has_requires(
        self,
        session: AsyncSession,
        *,
        roles: typing.Union[str, typing.Sequence[str]] = None,
        groups: typing.Union[str, typing.Sequence[str]] = None,
        permissions: typing.Union[str, typing.Sequence[str]] = None,
    ) -> bool:
        """
        check if user has rbac permission
        :param session:  sqlalchemy session
        :param roles: role list
        :param groups: group list
        :param permissions:  permission list
        :return: bool
        """
        stmt = select(1)
        if groups:
            groups_list = [groups] if isinstance(groups, str) else list(groups)
            stmt = stmt.where(self._has_groups(groups_list))
        if roles:
            roles_list = [roles] if isinstance(roles, str) else list(roles)
            stmt = stmt.where(self._has_roles(roles_list))
        if permissions:
            permissions_list = (
                [permissions] if isinstance(permissions, str) else list(permissions)
            )
            stmt = stmt.where(self._has_permissions(permissions_list))

        return bool(await session.execute(stmt).scalars().all())


class Group(Base, TimestampMixin):
    """auth user group table"""

    __tablename__ = "auth_group"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship(
        "User", secondary="auth_user_groups", back_populates="groups", overlaps="groups"
    )
    roles = relationship(
        "Role", secondary="auth_group_roles", back_populates="groups", overlaps="groups"
    )


class Role(Base, TimestampMixin):
    __tablename__ = "auth_role"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship(
        "User", secondary="auth_user_roles", back_populates="roles", overlaps="roles"
    )
    groups = relationship(
        "Group", secondary="auth_group_roles", back_populates="roles", overlaps="roles"
    )
    permissions = relationship(
        "Permission",
        secondary="auth_role_permissions",
        back_populates="roles",
        overlaps="roles",
    )


class Permission(Base, TimestampMixin):
    __tablename__ = "auth_permission"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    roles = relationship(
        "Role",
        secondary="auth_role_permissions",
        back_populates="permissions",
        overlaps="permissions",
    )