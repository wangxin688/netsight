from collections.abc import Sequence

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from netsight.core.errors.exception_handlers import NotFoundError, PermissionDenyError
from netsight.core.repositories import BaseRepository
from netsight.core.utils.context import locale_ctx
from netsight.features.admin import schemas
from netsight.features.admin.models import Group, Menu, Permission, Role, User
from netsight.features.admin.schemas import PermissionCreate, PermissionUpdate
from netsight.features.admin.security import verify_password

__all__ = (
    "user_service",
    "permission_service",
    "menu_service",
    "group_service",
    "role_service",
)


class UserService(BaseRepository[User, schemas.UserCreate, schemas.UserUpdate, schemas.UserQuery]):
    async def verify_user(self, session: AsyncSession, user: OAuth2PasswordRequestForm) -> User:
        stmt = self._get_base_stmt().where(or_(self.model.email == user.username))
        db_user = await session.scalar(stmt)
        if not db_user:
            raise NotFoundError(self.model.__visible_name__[locale_ctx.get()], "username", user.username)
        if not verify_password(user.password, db_user.password):
            raise PermissionDenyError
        db_user.last_login = func.now()
        session.add(db_user)
        await session.commit()
        return db_user


class PermissionService(
    BaseRepository[Permission, schemas.PermissionCreate, schemas.PermissionUpdate, schemas.PermissionQuery]
):
    async def create(
        self,
        session: AsyncSession,
        obj_in: PermissionCreate,
        excludes: set[str] | None = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        commit: bool | None = True,
    ) -> Permission:
        raise NotImplementedError

    async def update(
        self,
        session: AsyncSession,
        db_obj: Permission,
        obj_in: PermissionUpdate,
        excludes: set[str] | None = None,
        commit: bool | None = True,
    ) -> Permission:
        raise NotImplementedError

    async def delete(self, session: AsyncSession, db_obj: Permission) -> None:
        raise NotImplementedError

    async def get_all(self, session: AsyncSession) -> Sequence[Permission]:
        return (await session.scalars(select(self.model))).all()


class MenuService(BaseRepository[Menu, schemas.MenuCreate, schemas.MenuUpdate, schemas.MenuQuery]):
    async def get_all(self, session: AsyncSession) -> Sequence[Menu]:
        return (await session.scalars(select(self.model))).all()

    @staticmethod
    def menu_tree_transform(menus: Sequence[Menu]) -> list[dict]: ...


class GroupService(BaseRepository[Group, schemas.GroupCreate, schemas.GroupUpdate, schemas.GroupQuery]): ...


class RoleService(BaseRepository[Role, schemas.RoleCreate, schemas.RoleUpdate, schemas.RoleQuery]): ...


user_service = UserService(User)
permission_service = PermissionService(Permission)
menu_service = MenuService(Menu)
group_service = GroupService(Group)
role_service = RoleService(Role)
