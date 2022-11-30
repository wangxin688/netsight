from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth import schemas
from src.api.auth.models import Group, User
from src.api.base import BaseListResponse, BaseResponse
from src.api.deps import (
    CommonParams,
    audit_without_data,
    common_params,
    get_current_user,
    get_session,
)
from src.register.middleware import AuditRoute
from src.utils.error_code import (
    ERR_NUM_0,
    ERR_NUM_10004,
    ERR_NUM_10005,
    ERR_NUM_10006,
    ERR_NUM_10007,
)

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class AuthUserCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)

    @router.get(
        "/users/{id}",
    )
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
        users: schemas.AuthUserQuery | None,
        common_params: CommonParams = Depends(common_params),
    ) -> BaseListResponse[List[schemas.AuthUser]]:
        # TODO: confirm query_params
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
            select(User).where(User.id == id)
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
            groups: List[Group] = (
                (
                    await self.session.execute(
                        select(Group).where(Group.id.in_(user.auth_group_ids))
                    )
                )
                .scalars()
                .all()
            )
            group_ids = [group.id for group in groups]
            if len(group_ids) < len(user.auth_group_ids):
                not_existed_groups = set(group_ids) - set(user.auth_group_ids)
                return {
                    "code": ERR_NUM_10007,
                    "data": None,
                    "msg": f"Group {not_existed_groups} not existed",
                }
            for group in groups:
                local_user.auth_group.append(group)
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
        return_info = ERR_NUM_0.dict()
        name = group.name
        local_group: Group | None = (
            (await self.session.execute(select(Group).where(Group.name == name)))
            .scalars()
            .first()
        )
        if local_group is not None:
            return ERR_NUM_10006.dict()
        new_group = Group(**group.dict(exclude={"auth_user_ids"}))
        self.session.add(new_group)
        await self.session.commit()
        await self.session.flush()
        if not group.auth_user_ids:
            return_info["data"] = id
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
        user_ids = [user.id for user in users]
        if len(user_ids) < len(group.auth_user_ids):
            not_existed_users = set(user_ids) - set(group.auth_user_ids)
            return {
                "code": ERR_NUM_10004.code,
                "data": None,
                "msg": f"User {not_existed_users} not existed",
            }
        for user in users:
            new_group.auth_user.append(user)
        self.session.add(new_group)
        await self.session.commit()
        return_info["data"] = id
        return return_info

    @router.get("/groups/{id}")
    async def get_group(self, id: int) -> BaseResponse[schemas.AuthGroup]:
        results: AsyncResult = self.session.execute(
            select(Group).where(Group.id == id).options(selectinload(Group.auth_user))
        )
        group: Group | None = await results.scalars().first()
        if not group:
            return ERR_NUM_10007.dict()
        return_info = ERR_NUM_0(data=group)
        return return_info

    @router.get("/groups")
    async def get_groups(
        self,
        groups: schemas.AuthGroupQuery | None,
        common_params: CommonParams = Depends(common_params),
    ) -> BaseListResponse[List[schemas.AuthGroup]]:
        stm = select(Group)  # noqa
        cnt_stmt = select(func.count(Group.id))  # noqa

    @router.put("/groups/{id}")
    async def update_group(
        self,
        id: int,
        group: schemas.AuthGroupUpdate,
    ) -> BaseResponse[int]:
        result: AsyncResult = self.session.execute(
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
            users: List[User] = (
                (
                    await self.session.execute(
                        select(User).where(User.id.in_(group.auth_user_ids))
                    )
                )
                .scalars()
                .all()
            )
            user_ids = [user.id for user in users]
            if len(user_ids) < len(group.auth_user_ids):
                not_existed_users = set(user_ids) - set(group.auth_user_ids)
                return {
                    "code": ERR_NUM_10004.code,
                    "data": None,
                    "msg": f"User {not_existed_users} not existed",
                }
            for user in users:
                local_group.auth_user.append(user)
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
        result: AsyncResult = self.session.execute(select(Group).where(Group.id == id))
        local_group: Group | None = await result.scalars().first()
        if not local_group:
            return ERR_NUM_10007
        self.session.delete(local_group)
        await self.session.commit()
        return_info = ERR_NUM_0
        return_info.data = local_group.id
        return return_info
