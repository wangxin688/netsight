from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth import schemas
from src.api.auth.models import Group, Permission, Role, User
from src.api.base import BaseListResponse, BaseResponse, CommonQueryParams
from src.api.deps import audit_without_data, get_current_user, get_session
from src.register.middleware import AuditRoute
from src.utils.error_code import (
    ERR_NUM_0,
    ERR_NUM_10004,
    ERR_NUM_10005,
    ERR_NUM_10006,
    ERR_NUM_10007,
    ERR_NUM_10008,
    ERR_NUM_10009,
)

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class AuthUserCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)

    @router.get("/users/{id}")
    async def get_user(self, id: int) -> BaseResponse[schemas.AuthUser]:
        result: AsyncResult = await self.session.execute(
            select(User).where(User.id == id).options(selectinload(User.auth_role))
        )
        local_user: User | None = result.scalars().first()
        if not local_user:
            return ERR_NUM_10004.dict()
        return_info = ERR_NUM_0.dict()
        return_info["data"] = local_user
        return return_info

    @router.get("/users")
    async def get_users(
        self,
        users: schemas.AuthUserQuery = Depends(schemas.AuthUserQuery),
        common_params: CommonQueryParams = Depends(CommonQueryParams),
    ) -> BaseListResponse[List[schemas.AuthUser]]:
        if not common_params.q:
            result = (
                (
                    await self.session.execute(
                        select(User)
                        .slice(
                            common_params.offset,
                            common_params.limit + common_params.offset,
                        )
                        .options(selectinload(User.auth_role))
                    )
                )
                .scalars()
                .all()
            )
            count = (await self.session.execute(select(func.count(User.id)))).scalar()
            return_info = ERR_NUM_0.dict()
            return_info.update({"data": {"count": count, "results": result}})
            return return_info

    @router.put("/users/{id}")
    async def update_user(
        self,
        id: int,
        user: schemas.AuthUserUpdate,
    ) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(User).where(User.id == id).options(selectinload(User.auth_group))
        )
        local_user: User | None = result.scalars().first()
        if not local_user:
            return ERR_NUM_10004.dict()
        if user.email is not None:
            existed = (
                (
                    await (
                        self.session.execute(
                            select(User.id).where(User.email == user.email)
                        )
                    )
                )
                .scalars()
                .one_or_none()
            )
            if existed:
                return ERR_NUM_10005.dict()
        if user.auth_group_ids:
            groups: List[Group] = local_user.auth_group
            group_ids = [group.id for group in groups]
            for group in groups:
                if group.id not in user.auth_group_ids:
                    local_user.auth_group.remove(group)
            for user_group_id in user.auth_group_ids:
                if user_group_id not in group_ids:
                    auth_group: Group | None = (
                        (
                            await (
                                self.session.execute(
                                    select(Group).where(Group.id == user_group_id)
                                )
                            )
                        )
                        .scalars()
                        .one_or_none()
                    )
                    if auth_group:
                        local_user.auth_group.append(auth_group)
        if not user.password:
            await self.session.execute(
                update(User)
                .where(User.id == id)
                .values(
                    **user.dict(
                        exclude_none=True, exclude={"auth_group_ids"}
                    ).execute_options(synchronize_session="fetch")
                )
            )
        else:
            await self.session.execute(
                update(User)
                .where(User.id == id)
                .values(
                    **user.dict(
                        exclude_none=True, exclude={"auth_group_ids", "password2"}
                    ).execute_options(synchronize_session="fetch")
                )
            )
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = local_user.id
        return return_info

    @router.delete("/users/{id}")
    async def delete_user(self, id: int) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(User).where(User.id == id)
        )
        local_user: User | None = result.scalars().first()
        if not local_user:
            return ERR_NUM_10004.dict()
        await self.session.delete(local_user)
        await self.session.commit()
        return_info = ERR_NUM_0.dict()
        return_info.update({"data": id})
        return return_info


@cbv(router)
class AuthGroupCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)

    @router.post("/groups")
    async def create_group(
        self, group: schemas.AuthGroupCreate
    ) -> BaseResponse[int | None]:
        return_info = ERR_NUM_0
        local_group: Group | None = (
            (await self.session.execute(select(Group).where(Group.name == group.name)))
            .scalars()
            .first()
        )
        if local_group is not None:
            return ERR_NUM_10006
        new_group = Group(**group.dict(exclude={"auth_user_ids"}))
        self.session.add(new_group)
        await self.session.flush()
        if not group.auth_user_ids:
            await self.session.commit()
            return_info.data = id
            return return_info
        users: List[User] = (
            (
                await self.session.execute(
                    select(User).where(User.id.in_(group.auth_user_ids))
                )
            )
            .scalars()
            .all()
        )
        for user in users:
            new_group.auth_user.append(user)
        self.session.add(new_group)
        await self.session.commit()
        return_info.data = id
        return return_info

    @router.get("/groups/{id}")
    async def get_group(self, id: int) -> BaseResponse[schemas.AuthGroup]:
        results: AsyncResult = await self.session.execute(
            select(Group).where(Group.id == id).options(selectinload(Group.auth_user))
        )
        group: Group | None = results.scalars().first()
        if not group:
            return ERR_NUM_10007
        return_info = ERR_NUM_0(data=group)
        return return_info

    @router.get("/groups")
    async def get_groups(
        self,
        groups: schemas.AuthGroupQuery = Depends(),
        common_params: CommonQueryParams = Depends(CommonQueryParams),
    ) -> BaseListResponse[List[schemas.AuthGroup]]:
        stm = select(Group)  # noqa
        cnt_stmt = select(func.count(Group.id))  # noqa

    @router.put("/groups/{id}")
    async def update_group(
        self,
        id: int,
        group: schemas.AuthGroupUpdate,
    ) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(
                select(Group)
                .where(Group.id == id)
                .options(selectinload(Group.auth_user))
            )
        )
        local_group: Group | None = result.scalars().first()
        if not local_group:
            return ERR_NUM_10007
        if group.auth_user_ids:
            users: List[User] = local_group.auth_user
            user_ids = [user.id for user in users]
            for user in users:
                if user.id not in group.user_ids:
                    local_group.auth_user.remove(user)
            for auth_user_id in group.auth_user_ids:
                if auth_user_id not in user_ids:
                    _auth_user: User | None = (
                        (
                            await self.session.execute(
                                select(User).where(User.id == auth_user_id)
                            )
                        )
                        .scalars()
                        .one_or_none()
                    )
                    if _auth_user:
                        local_group.auth_user.append(_auth_user)
        self.session.execute(
            update(Group)
            .where(Group.id == id)
            .values(**group.dict(exclude={"auth_user_ids"}, exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = local_group.id
        return return_info

    @router.delete("/groups/{id}")
    async def delete_group(self, id: int) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(Group).where(Group.id == id)
        )
        local_group: Group | None = result.scalars().first()
        if not local_group:
            return ERR_NUM_10007
        self.session.delete(local_group)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = local_group.id
        return return_info


@cbv(router)
class AuthRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)

    @router.post("/roles")
    async def create_role(
        self,
        role: schemas.AuthRoleCreate,
    ) -> BaseResponse[int]:
        return_info = ERR_NUM_0
        local_role: Role | None = (
            (await self.session.execute(select(Role).where(Role.name == role.name)))
            .scalars()
            .first()
        )
        if local_role is not None:
            return ERR_NUM_10008

        new_role = Role(**role.dict(exclude={"auth_user_ids", "auth_permission_ids"}))
        self.session.add(new_role)
        await self.session.flush()
        if role.auth_permission_ids:
            permissions = List[Permission] = (
                (
                    await self.session.execute(
                        select(Permission).where(
                            Permission.id.in_(role.auth_permission_ids)
                        )
                    )
                )
                .scalars()
                .all()
            )
            if permissions:
                for permission in permissions:
                    new_role.auth_permission.append(permission)
        await self.session.commit()
        return_info.data = new_role.id
        return return_info

    @router.get("/roles/{id}")
    async def get_role(self, id: int) -> BaseResponse[schemas.AuthRole]:
        results: AsyncResult = await self.session.execute(
            select(Role)
            .where(Role.id == id)
            .options(selectinload(Role.auth_permission))
        )
        role: Role | None = results.scalars().first()
        if not role:
            return ERR_NUM_10009
        return_info = ERR_NUM_0(data=role)
        return return_info

    @router.get("/roles")
    async def get_roles(
        self,
        roles: schemas.AuthRoleQuery = Depends(),
        common_params: CommonQueryParams = Depends(CommonQueryParams),
    ) -> BaseListResponse[List[schemas.AuthRole]]:
        stm = select(Group)  # noqa
        cnt_stmt = select(func.count(Group.id))  # noqa

    @router.put("/roles/{id}")
    async def update_role(
        self,
        id: int,
        role: schemas.AuthRoleUpdate,
    ) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(
                select(Role)
                .where(Role.id == id)
                .options(selectinload(Role.auth_permission))
            )
        )
        local_role: Role | None = result.scalars().first()
        if not local_role:
            return ERR_NUM_10009
        if role.auth_permission_ids:
            permissions: List[Permission] = local_role.auth_permission
            permission_ids = [permission.id for permission in permissions]
            for permission in permissions:
                if permission.id not in role.auth_permission_ids:
                    local_role.auth_permission.remove(permission)
            for auth_permission_id in role.auth_permission_ids:
                if auth_permission_id not in permission_ids:
                    _auth_permission: Permission | None = (
                        (
                            await self.session.execute(
                                select(Permission).where(
                                    Permission.id == auth_permission_id
                                )
                            )
                        )
                        .scalars()
                        .one_or_none()
                    )
                    if _auth_permission:
                        local_role.auth_user.append(_auth_permission)
        self.session.execute(
            update(Role)
            .where(Role.id == id)
            .values(**role.dict(exclude={"auth_permission_ids"}, exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = local_role.id
        return return_info

    @router.delete("/roles/{id}")
    async def delete_role(self, id: int) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(Role).where(Role.id == id)
        )
        local_role: Role | None = result.scalars().first()
        if not local_role:
            return ERR_NUM_10007
        self.session.delete(local_role)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = local_role.id
        return return_info
